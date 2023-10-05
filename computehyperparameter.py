import chunk
from compute_files import ComputeFile
from deep_similarity import DeepSimilarity
from get_format import get_format
from matrixhandling import MatrixHandling
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
import numpy as np
from reformulation import Reformulation
from string_utils import StringUtils
from collections import Counter
import os

class Hyperparameter:
    
    def __init__(self, source_file='', target_file='', training_file=''):
        self.source_file = source_file
        self.target_file = target_file
        self.training_file = training_file
        self.datasets_measured = []
        self.start_time = time.time()
        log.info('###   Hyperparameter computation started    ###')
    
    def build_graph(self, input_file=''):
        graph = Graph()
        print(input_file)
        graph.parse(input_file, format=get_format(value=input_file))
        return graph
    
    def get_links(self, graph=None):
        query = """SELECT ?fsubject ?fobject
                   WHERE {
                    ?fsubject  ?fpredicate  ?fobject .
                    }
                """
        results = graph.query(query)
        for data in results :
            if str(data['fobject']) != 'http://www.w3.org/2002/07/owl#sameAs' :
                self.datasets_measured.append({
                    'source': str(data['fsubject']),
                    'target': str(data['fobject']),
                    'predicates': [], # [[param1, param2, param3], ...]
                    'literals': [] # [[param1, param2, param3], ...]
                })
        return self.datasets_measured
    
    def get_entity_from_graph(self, graph=None, entity=None):
        output = {}
        query = """SELECT ?fpredicate ?fobject
                   WHERE {
                    <?fsubject>  ?fpredicate  ?fobject .
                    }
                """
        query = query.replace('?fsubject', entity)
        results = graph.query(query)
        for data in results :
            predicate = str(data['fpredicate'])
            object = str(data['fobject'])
            if not (validators.url(object) or ('#type' in predicate)):
                if not predicate in output:
                    output[predicate] = []
                output[predicate].append(object)
        return output # { predicate: [object1, ... ,objectn]}
    
    def get_percents(self, value1='', value2=''):
        ds = DeepSimilarity(code='*')
        lcs, hamming = ds._comparison(first=value1, second=value2)
        return (lcs, hamming)

    
    def update_measurements(self, dataset=[], sentity='', tentity='', type='', values=[]):
        output = []
        for data in dataset:
            if data['source'] == sentity and data['target'] == tentity :
                if not type in data:
                    data[type] = [] 
                data[type].append(values)
            output.append(data)
        return output
    
    def frequent_value(self, data=[], output=[]):
        tmp = data
        if len(tmp) > 0 :
            a = Counter(tmp)
            mc = a.most_common(1)
            if len(mc) > 0 :
                mc = mc[0]
            tmp = list(filter(lambda x: x!= mc[0], tmp))
            output.append(mc)
            return self.frequent_value(data=tmp, output=output)
        else:
            return output
    
    def normalze_features(self, values=[], predicates_couples=[]):
        max_len_pred = max([len(value['predicates']) for value in values])
        max_len_literals = max([len(value['literals']) for value in values])
        _predicates = []
        _literals = []
        for value in values:
            tmp_pred = value['predicates']
            tmp_obj = value['literals']
            # print(max_len_pred, ' ------------- ', len(tmp_pred))
            if max_len_pred-len(tmp_pred) > 0 :
                tmp_pred = tmp_pred + [(0.0, 0.0) for _ in range(max_len_pred-len(tmp_pred))]
            value['predicates'] = tmp_pred
            # print(value['predicates'])
            
            # print(max_len_literals, ' ------------- ', len(tmp_obj))
            if max_len_literals-len(tmp_obj) > 0 :
                tmp_obj = tmp_obj + [(0.0, 0.0) for _ in range(max_len_literals-len(tmp_obj))]
            value['literals'] = tmp_obj
            # print(value['literals'])
            # exit()
            _predicates.append(value['predicates'])
            _literals.append(value['literals'])
        dataname, _output, good_predicates = MatrixHandling(ptensors=_predicates, ltensors=_literals, predicates_couples=predicates_couples, output_path=os.path.dirname(self.target_file)).run()
        params = "--alpha_predicate {} --alpha {} --phi {} --measure_level {}"
        params = params.format(_output['ceil_p'], _output['ceil_o'], int(_output['threshold_acceptance']), _output['depth_o'])
        print(' \n Global Predicates count : ', len(list(set(predicates_couples))), ' Selected predicates count : ', len(good_predicates))
        _params = "\n sh ./job.sh --input_source ./inputs/[data_name]/sourcef --input_target ./inputs/[data_name]/targetf --output ./outputs/[data_name]/ " + params + " --validation ./validations/[data_name]/valid_same_as.ttl"
        _params = _params.replace('[data_name]', dataname)
        
        print('\n ++++++++++++++++++++++++++++++++++++')
        print('Command to process on real data # \n ')
        print('\n \n')
        print(_params)
        
    def run(self):
        start_time = time.time()
        source_graph = self.build_graph(input_file=self.source_file)
        target_graph = self.build_graph(input_file=self.target_file)
        training_graph = self.build_graph(input_file=self.training_file)
        matching = self.get_links(graph=training_graph)
        _predicates_percents = []
        _literals_percents = []
        predicates_couples = []
        for couple in matching :
            source_entity = self.get_entity_from_graph(graph=source_graph, entity=couple['source'])
            target_entity = self.get_entity_from_graph(graph=target_graph, entity=couple['target'])
            if len(source_entity.keys()) > 0 and len(target_entity.keys()) > 0 :
                for spred in source_entity:
                    for tpred in target_entity:
                        tmp_percents = self.get_percents(value1=spred, value2=tpred)
                        # print('predicate level: ', tmp_percents)
                        _predicates_percents = _predicates_percents + [tmp_percents]
                        self.datasets_measured = self.update_measurements(dataset=self.datasets_measured, sentity=couple['source'], tentity=couple['target'], type='predicates', values=tmp_percents)
                        predicates_couples.append((spred, tpred))
                        for svalue in source_entity[spred] :
                            for tvalue in target_entity[tpred] :
                                tmp_percents = self.get_percents(value1=svalue, value2=tvalue)
                                # print('\t objects level : ', tmp_percents)
                                _literals_percents = _literals_percents + [tmp_percents]
                                self.datasets_measured = self.update_measurements(dataset=self.datasets_measured, sentity=couple['source'], tentity=couple['target'], type='literals', values=tmp_percents)           
        print("--- %s seconds ---" % (time.time() - start_time))
        print('Process ended')
        self.normalze_features(values=self.datasets_measured, predicates_couples=predicates_couples)
        
        
if __name__ == '__main__' :
    def arg_manager():
        parser = argparse.ArgumentParser()
        parser.add_argument("--source_file", type=str, default="./inputs/spaten_hobbit/source.nt")
        parser.add_argument("--target_file", type=str, default="./inputs/spaten_hobbit/target.nt")
        parser.add_argument("--training_file", type=str, default="./validations/spaten_hobbit/valid_same_as.ttl")
        return parser.parse_args()
    args = arg_manager()
    training = args.training_file
    if args.training_file.split('.')[-1] == 'ttl' :
        training = args.training_file
    valid = Reformulation(input_file=training).run()
    Hyperparameter(source_file=args.source_file, target_file=args.target_file, training_file=training).run()

# python3.8 ./computehyperparameter.py --source_file ./inputs/spaten_hobbit/source.nt --target_file ./inputs/spaten_hobbit/target.nt --training_file ./validations/spaten_hobbit/valid_same_as.nt
# python3.8 ./computehyperparameter.py --source_file ./inputs/doremus/source.nt --target_file ./inputs/doremus/target.nt --training_file ./validations/doremus/valid_same_as.nt