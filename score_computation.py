import chunk
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
import pandas as pd
import time
import argparse
from reformulation import Reformulation


class ScoreComputation:
    
    def __init__(self, input_good_validation='', input_bad_validation='', input_same_as_file='', chunk_size=1000):
        self.input_good_validation = input_good_validation
        self.input_bad_validation = input_bad_validation
        self.input_same_as_file = input_same_as_file
        self.chunk_size = chunk_size
        self.recaps = {
            '00': 0,
            '01': 0,
            '10': 0,
            '11': 0,
            'precision': 0,
            'recall': 0,
            'fmeasure': 0
        }
        self.start_time = time.time()
        log.info('###   Score Analysis started    ###')
    
    def build_graph(self, input_file=''):
        graph = Graph()
        graph.parse(input_file, format=get_format(value=input_file))
        return graph
    
    def get_positive_links(self, graph=None):
        query = """SELECT DISTINCT (count(?fsubject) as ?fcount)
                    WHERE {
                    ?fsubject  ?fpredicate  ?fobject .
                    }
                """
        results = graph.query(query)
        for _count in results:
            self.recaps['positives'] = int(str(_count['fcount']))
            # self.recaps['00'] = int(str(_count['fcount']))
        print('True fact : ' , self.recaps['positives'])
        return 
    
    def get_link(self, graph=None, _fsubject='', _ssubject='', has_matched=None, recaps={}):
        query = """SELECT (count(?fpredicate) as ?fcount)
                    WHERE {
                    <?fsubject> ?fpredicate <?fobject>  .
                    }
                """
        query = query.replace('?fsubject', _fsubject)
        query = query.replace('?fobject', _ssubject)
        results = graph.query(query)
        for _count in results:
            fcount = int(str(_count['fcount'])) 
            if  fcount > 0:
                key = str(has_matched) + '1'
            else:
                key = '0' + str(has_matched)
            recaps[key] += 1
        return recaps
    
    def treat_links(self, data=None, graph=None, recaps={}):
        for _, row in data.iterrows():
            fsubject = row['fsubject']
            ssubject = row['ssubject']
            has_matched = row['has_matched']
            recaps = self.get_link(graph=graph, _fsubject=fsubject, _ssubject=ssubject, has_matched=has_matched, recaps=recaps)
        return recaps
    
    def new_treat_links(self, data=None, graph=None, recaps={}):
        fsubject, ssubject = data
        has_matched = 1
        tmp_recaps = self.get_link(graph=graph, _fsubject=fsubject, _ssubject=ssubject, has_matched=has_matched, recaps=recaps)
        return tmp_recaps
    
    def feedback(self, input_file='', graph=None):
        _tmp_graph = self.build_graph(input_file=input_file)
        tmp_recaps = self.recaps
        for s, _, o in _tmp_graph:
            tmp_recaps = self.new_treat_links(data=(s,o),graph=graph,recaps=tmp_recaps)
        self._recapitulating(recaps=tmp_recaps)
        return tmp_recaps
            
    def chuncked_treatment(self, input_file='', graph=None):
        pool = multiprocessing.Pool()
        # parallel computing
        recaps = self.recaps
        result_async = [pool.apply_async(self.treat_links, args =(chunked_data, graph, recaps, )) for chunked_data in pd.read_csv(input_file, 
                                                header=None, names=['fsubject', 'ssubject', 'fobject', 'sobject', 'has_matched'],
                                                chunksize=self.chunk_size)]
        for _result in result_async :
            _res = _result.get()
            for param in _res:
                recaps[param] += _res[param]
        
        self._recapitulating(recaps=recaps)
    
    def _recapitulating(self, recaps={}):
        tn = recaps['00']
        fp = recaps['01']
        fn = self.recaps['positives'] - (recaps['11'])
        self.recaps['10'] = fn
        tp = recaps['11']
        try:
            precision = (tp) / (tp + fp)
            recall = (tp) / (tp + fn)
            fmeasure = (2*precision*recall) / (precision + recall)
        except ZeroDivisionError:
            precision = 0
            recall = 0
            fmeasure = 0
        self.recaps['precision'] = precision
        self.recaps['recall'] = recall
        self.recaps['fmeasure'] = fmeasure
        print(self.recaps)
        print('------------------------')
        print('Precision : ', precision)
        print('Recall : ', recall)
        print('Fmeasure : ', fmeasure)
        
    
    def run(self):
        start_time = time.time()
        graph = self.build_graph(input_file=self.input_same_as_file)
        self.get_positive_links(graph=graph)
        self.feedback(input_file=self.input_good_validation, graph=graph)
        print('Process ended')
        print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__' :
    def arg_manager():
        parser = argparse.ArgumentParser()
        parser.add_argument("--input_source", type=str, default="./inputs/doremus/source.ttl")
        parser.add_argument("--input_target", type=str, default="./inputs/doremus/target.ttl")
        parser.add_argument("--output_path", type=str, default="./outputs/doremus/")
        parser.add_argument("--alpha_predicate", type=float, default=1)
        parser.add_argument("--alpha", type=float, default=0.88)
        parser.add_argument("--phi", type=int, default=2)
        parser.add_argument("--measure_level", type=int, default=1)
        parser.add_argument("--validation", type=str, default="./validations/doremus/valid_same_as.ttl")
        return parser.parse_args()
    args = arg_manager()
    valid = args.validation
    if args.validation.split('.')[-1] == 'ttl' :
        valid = args.validation
    else:
        valid = Reformulation(input_file=args.validation).run()
    ScoreComputation(input_good_validation=args.output_path + 'same_as_entities.ttl', 
                input_same_as_file=valid, chunk_size=1000).run()
    