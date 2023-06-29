
from typing import Optional
from compute_files import ComputeFile
from deep_similarity import DeepSimilarity
from get_format import get_format
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
from multiprocessing import Manager
import time
import hashlib
from datetime import datetime
from dateutil import tz
import argparse
import os
import locale
os.environ["PYTHONIOENCODING"] = "utf-8"
scriptLocale=locale.setlocale(category=locale.LC_ALL, locale="en_GB.UTF-8")


def divide_chunks(l, n):
    outputs = [] 
    data = list(l)
    for i in range(0, len(data), n):
        outputs.append(data[i:i + n])
    return outputs

class CandidateEntityPairs:
    
    def __init__(self, input_source='',  input_target='', output_path='', similar_predicates_path='', alpha=0, phi=0, level=1):
        log.info("Candidates Entities Pairs started ")
        self.predicates_pairs = self.read_similar_predicates(file_name=similar_predicates_path)
        self.input_source = input_source
        self.input_target = input_target
        self.output_path = output_path
        self.input_files = []
        self.limit = 10
        self.start_time = time.time()
        self.local_time = datetime.now(tz.gettz())
        self.alpha = alpha
        self.phi = phi
        self.level = level
        print('----------- ', self.local_time, ' -----------')
        log.info('###   Predicates similarities started    ###')
    
    def build_graph(self, input_file=''):
        graph = Graph()
        graph.parse(input_file, format=get_format(value=input_file))
        return graph
    
    def can_save_pair(self, key='', recaps={}):
        _key = key # base64.b64encode((key).encode('utf-8')).decode('utf-8')
        if not _key in recaps[1]:
            recaps[1][_key] = 0
        if _key in recaps[1]:
            recaps[1][_key] = recaps[1][_key] + 1
            stat = recaps[1][_key]
            if stat >= self.phi :
                return True
        return False
    
    def get_entities(self, graph=None, predicate=''):
        outputs = []
        query = """SELECT DISTINCT ?fsubject ?fobject
                    WHERE {?fsubject  :fpredicate  ?fobject .}
                """
        query = query.replace(':fpredicate', predicate)
        results = graph.query(query)
        for _predicate in results:
            if not validators.url(_predicate['fobject']) or ('#type' in predicate):
                outputs.append((_predicate['fsubject'], _predicate['fobject']))
        return outputs
    
    def read_similar_predicates(self, file_name=''):
        return dump().read_csv(file_name=file_name)
    
    def insert_to_graph(self, graph=None, fsubject='', ssubject=''):
        query = """INSERT DATA {  <?psubject> owl:sameAs  <?pobject> .  }"""
        query = query.replace('?psubject', fsubject).replace(
            '?pobject', ssubject)
        try:
            graph.update(query)                       
        except ParseException as _:
            log.critical('Exception during updating graph')
        return graph        
    
    def leastOneIn(self, value1='', value2='', alpha=0.0):
        tmp_one = value1.split(' ');
        count = 0
        for tmp in tmp_one : 
            if tmp in value2 :
                count = count + 1
        count = count/len(tmp_one)
        if count > alpha :
            return True
        return False
    
    def sub_treatments(self, pairs=[], alpha=0, _recaps={}):
        ds = DeepSimilarity(code='*')
        good_entities_pairs = []
        messages = []
        _alpha = alpha
        graph = Graph()
        for first_so, second_so in pairs:
            fs, fo = first_so
            ss, so = second_so
            if self.leastOneIn(value1=fo, value2=so, alpha=alpha):
                if ds.comparison_run(first=fo, second=so, alpha=_alpha, level=self.level) and self.can_save_pair(key=(fs + ss), recaps=_recaps):
                    good_entities_pairs.append((fs, ss, fo, so, 1))
                    message = '<' + fs + '>\t<http://www.w3.org/2002/07/owl#sameAs>\t<' + ss + '>\t.'
                    dump().write_to_txt(file_path='./outputs/logs/links.txt', values=[message])
                    graph = self.insert_to_graph(graph=graph, fsubject=fs, ssubject=ss)
                    messages.append(message)
        return graph, messages, good_entities_pairs

    def treat_entities_pairs(self, entities_pairs=[], alpha=0.0, recaps={}):
        tmp_entities_pairs = entities_pairs
        good_entities_pairs = []
        bad_entities_pairs = []
        messages = []
        graph = Graph()
        good_entities_pairs = []
        pool = multiprocessing.Pool()
        cpu = multiprocessing.cpu_count()
        result_async = [pool.apply_async(self.sub_treatments, args=(pairs, alpha, recaps)) for pairs in divide_chunks(tmp_entities_pairs, cpu)]
        for result_entities_pairs in result_async :
            _res_graphs, _messages, _good_entities_pairs = result_entities_pairs.get()
            messages = messages + _messages
            good_entities_pairs = good_entities_pairs + _good_entities_pairs
            graph = graph + _res_graphs
        return [graph, good_entities_pairs, bad_entities_pairs]

    def process_by_pairs_predicates(self,row=[], graphs=[], _recaps={}):
        entities = []
        graph = None
        good_entities_pairs = []
        bad_entities_pairs = []
        for i in range(len(graphs)):
            predicate = row['predicate_' + str(i+1)]
            entities.append(self.get_entities(graph=graphs[i], predicate=predicate))
        tmp_entities_pairs = itertools.product(entities[0],entities[1])
        graph, good_entities_pairs, bad_entities_pairs = self.treat_entities_pairs(entities_pairs=tmp_entities_pairs, alpha=self.alpha, recaps=_recaps)
        return [graph, good_entities_pairs, bad_entities_pairs]
    
    def run(self):
        resulting_alignment = []
        graphs = ComputeFile(input_path='./inputs/', output_path=self.output_path).build_graph_from_files(source=self.input_source, target=self.input_target)
        predicates = self.predicates_pairs
        to_delete = [self.output_path + 'good_to_validate.csv', self.output_path + 'bad_to_validate.csv']
        _graphs = Graph()
        for file in to_delete:
            if os.path.isfile(file) :
                os.remove(file)
        # manager = Manager()
        _recaps = [{}, {}] # manager.dict()
        _recaps[0] = {}
        _recaps[1] = {}
        for _, predicate in predicates.iterrows():
            _res_graphs, _good_entities_pairs, _bad_entities_pairs = self.process_by_pairs_predicates(predicate, graphs, _recaps)
            for fs, ss, _, _, hm in _good_entities_pairs:
                resulting_alignment = resulting_alignment + [(str(fs), str(ss), '=', str(hm))]
                _graphs = _graphs + _res_graphs
                dump().write_tuples_to_csv(file_name=self.output_path + 'good_to_validate', data=_good_entities_pairs, columns=['fsubject', 'ssubject', 'fobject', 'sobject', 'has_matched'])
                dump().write_tuples_to_csv(file_name=self.output_path + 'bad_to_validate', data=_bad_entities_pairs, columns=['fsubject', 'ssubject', 'fobject', 'sobject', 'has_matched'])
        _graphs.serialize(destination=self.output_path + 'same_as_entities.ttl', format='turtle')
        self.local_time = datetime.now(tz.gettz())
        print('----------- END : ', self.local_time, ' -----------')
        print("--- %s seconds ---" % (time.time() - self.start_time))

if __name__ == '__main__' :
    def arg_manager():
        parser = argparse.ArgumentParser()
        parser.add_argument("--input_source", type=str, default="./inputs/doremus/source.nt")
        parser.add_argument("--input_target", type=str, default="./inputs/doremus/target.nt")
        parser.add_argument("--output_path", type=str, default="./outputs/doremus/")
        parser.add_argument("--alpha_predicate", type=float, default=1)
        parser.add_argument("--alpha", type=float, default=0.88)
        parser.add_argument("--phi", type=int, default=2)
        parser.add_argument("--measure_level", type=int, default=1)
        parser.add_argument("--validation", type=str, default="./validations/doremus/valid_same_as.ttl")
        return parser.parse_args()
    args = arg_manager()
    CandidateEntityPairs(input_source=args.input_source, input_target=args.input_target, output_path=args.output_path, similar_predicates_path=args.output_path + 'similars_predicates.csv', alpha=args.alpha, phi=args.phi, level=args.measure_level).run()
