
from compute_files import ComputeFile
from deep_similarity import DeepSimilarity
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF
from pyparsing import ParseException
from itertools import combinations
import itertools
import log
from decimal import *
from dump import dump
import validators
import base64
import multiprocessing
import time
import hashlib
from datetime import datetime
from dateutil import tz
import argparse
import os
import locale
os.environ["PYTHONIOENCODING"] = "utf-8"
scriptLocale=locale.setlocale(category=locale.LC_ALL, locale="en_GB.UTF-8")

class CandidateEntityPairs:
    
    def __init__(self, input_path='', output_path='', similar_predicates_path='', alpha=0, phi=0, measure='low'):
        log.info("Candidates Entities Pairs started ")
        self.predicates_pairs = self.read_similar_predicates(file_name=similar_predicates_path)
        self.input_path = input_path
        self.output_path = output_path
        self.input_files = []
        self.recapitulating = {}
        self.limit = 10
        self.start_time = time.time()
        self.local_time = datetime.now(tz.gettz())
        self.alpha = alpha
        self.phi = phi
        self.measure = measure
        print('----------- ', self.local_time, ' -----------')
        log.info('###   Predicates similarities started    ###')
    
    def can_save_pair(self, key=''):
        _key = base64.b64encode((key).encode('utf-8')).decode('utf-8')
        if not _key in self.recapitulating:
            self.recapitulating[_key] = 0
        if _key in self.recapitulating:
            self.recapitulating[_key] += 1
            stat = self.recapitulating[_key]
            if stat >= self.phi :
                return True
        # self.recapitulating[_key] = 1
        return False
    
    def get_entities(self, graph=None, predicate=''):
        outputs = []
        query = """SELECT DISTINCT ?fsubject ?fobject
                    WHERE {
                    ?fsubject  :fpredicate  ?fobject .
                    }
                """
        query = query.replace(':fpredicate', predicate)
        results = graph.query(query)
        for _predicate in results:
            if not validators.url(_predicate['fobject']) :
                outputs.append((_predicate['fsubject'], _predicate['fobject']))
        return outputs
    
    def read_similar_predicates(self, file_name=''):
        return dump().read_csv(file_name=file_name)
    
    def insert_to_graph(self, graph=None, fsubject='', ssubject=''):
        query = """INSERT DATA {  <?psubject> owl:sameAs  <?pobject> .  }"""
        query = query.replace('?psubject', fsubject).replace(
            '?pobject', ssubject)
        # print(query)
        try:
            graph.update(query)                       
        except ParseException as _:
            log.critical('Exception during updating graph')
        return graph        
    
    def treat_entities_pairs(self, entities_pairs=[]):
        tmp_entities_pairs = entities_pairs
        good_entities_pairs = []
        bad_entities_pairs = []
        graph=Graph()
        for first_so, second_so in tmp_entities_pairs:
            compare = DeepSimilarity(code='*')
            fs, fo = first_so
            ss, so = second_so
            if compare.comparison_run(first=fo, second=so, alpha=self.alpha, measure=self.measure) and self.can_save_pair(key=(fs + ss)) :
                good_entities_pairs.append((fs, ss, fo, so, 1))
                graph = self.insert_to_graph(graph=graph, fsubject=fs, ssubject=ss)
        return [graph, good_entities_pairs, bad_entities_pairs]
    
    def process_by_pairs_predicates(self,row=[], graphs=[]):
        entities = []
        graph = None
        good_entities_pairs = []
        bad_entities_pairs = []
        for i in range(len(graphs)):
            entities.append(self.get_entities(graph=graphs[i], predicate=row['predicate_' + str(i+1)]))
        tmp_entities_pairs = itertools.product(entities[0],entities[1])
        graph, good_entities_pairs, bad_entities_pairs = self.treat_entities_pairs(entities_pairs=tmp_entities_pairs)
        return [graph, good_entities_pairs, bad_entities_pairs]
    
    def run(self):
        print('Started')
        _, _, graphs = ComputeFile(input_path=self.input_path, output_path=self.output_path).build_list_files()
        predicates = self.predicates_pairs
        bad_entities_pairs = []
        good_entities_pairs = []
        _graphs = Graph()
        stop = 0
        pool = multiprocessing.Pool()
        # parallel computing
        result_async = [pool.apply_async(self.process_by_pairs_predicates, args =(row, graphs, )) for index, row in predicates.iterrows()]
        for result_entities_pairs in result_async :
            _res_graphs, _good_entities_pairs, _bad_entities_pairs = result_entities_pairs.get()
            _graphs = _graphs + _res_graphs
            good_entities_pairs = good_entities_pairs + _good_entities_pairs
            bad_entities_pairs = bad_entities_pairs + _bad_entities_pairs
            # if stop == self.limit :
            #     break
            # stop += 1
        _graphs.serialize(destination='./outputs/same_as_entities.ttl', format='turtle')
        dump().write_tuples_to_csv(file_name='./outputs/good_to_validate', data=good_entities_pairs, columns=['fsubject', 'ssubject', 'fobject', 'sobject', 'has_matched'])
        dump().write_tuples_to_csv(file_name='./outputs/bad_to_validate', data=bad_entities_pairs, columns=['fsubject', 'ssubject', 'fobject', 'sobject', 'has_matched'])
        print('Process ended')
        self.local_time = datetime.now(tz.gettz())
        print('----------- END : ', self.local_time, ' -----------')
        print("--- %s seconds ---" % (time.time() - self.start_time))

if __name__ == '__main__' :
    def arg_manager():
        parser = argparse.ArgumentParser()
        parser.add_argument("--alpha_predicate", type=float, default=1)
        parser.add_argument("--alpha", type=float, default=0.88)
        parser.add_argument("--phi", type=int, default=2)
        parser.add_argument("--measure", type=str, default='low')
        return parser.parse_args()
    args = arg_manager()
    CandidateEntityPairs(input_path='./inputs/', output_path='./outputs/', similar_predicates_path='./outputs/similars_predicates.csv', alpha=args.alpha, phi=args.phi, measure=args.measure).run()
