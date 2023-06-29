

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
import time
from cache import Cache
import multiprocessing
import pandas as pd


class GenerateSource:
    
    def __init__(self, input_file='', path_destination='', chunk_size=1000, must_augment=False):
        self.input_file = input_file
        self.path_destination = path_destination
        self.chunk_size = chunk_size
        self.must_augment = must_augment
        print('Generate Source started !')
    
    def load_graph(self, input_file=''):
        """
            expands the data and puts the new version in the associated output file
        """
        g = Graph()
        try:
            g.parse(input_file)
        except Exception as _ :
            log.critical('#Not converted to graph >> ' + input_file + ' ....%')
            return None
        return g

    def insert_data(self,  graph=None, _subject='', _predicate='', _new_object=''):
        query = """INSERT DATA { <?subject>  <?predicate>    ?object . }"""
        query = query.replace('?subject', _subject).replace('?predicate',  _predicate)
        query_result = None
        try:
            if validators.url(_new_object):
                query = query.replace('?object', '<' + (_new_object) + '>')
            else:
                query = query.replace('?object', '"' + (_new_object) + '"' )
            dump().write_to_txt(file_path='./outputs/motifs/insert_queries.txt', values=['Query 0', query])
            query_result = graph.update(query)
            if query_result != None :
                log.critical("Model 0 : Error when Updating : " + _subject + ' ' + _predicate + ' ' + _new_object )
        except ParseException as _:
            log.critical('Model 0 : Exception during updating graph')
        return graph 

    def indexing(self, uri=''):
            """[indexes the value in the cache]
            Args:
                uri (str): [url of the computed resource] | uri = 'http://purl.obolibrary.org/obo/TO_0000691'

            Returns:
                [str, array]: uri,  list of {p: '_value', o: '_value'} | ([{p: v, o: v'}, ...] )
            """
            #
            if not validators.url(uri):
                return '', []
            res, data = Cache().get_ressource(uri=uri)
            return res, data

    def treat_links(self, data=None, graph=None):
        _graph = graph
        for _, row in data.iterrows():
            # fsubject = row['s']
            # fpredicate = row['p']
            if self.must_augment :
                fobject = row['o']
                _, datas = self.indexing(uri=fobject)
                # insert into the graph
                for data in datas :
                    _predicate = data['p']
                    _object = data['o']
                    _graph = self.insert_data(graph=_graph, _subject=fobject, _predicate=_predicate, _new_object=_object)
            else:
                fsubject = row['s']
                fpredicate = row['p']
                fobject = row['o']
                _graph = self.insert_data(graph=_graph, _subject=fsubject, _predicate=fpredicate, _new_object=fobject)
        return _graph
                
    def convert_csv_to_graph(self, input_file=''):
        pool = multiprocessing.Pool()
        # parallel computing
        _graph = Graph()
        result_async = [pool.apply_async(self.treat_links, args =(chunked_data, _graph, )) for chunked_data in pd.read_csv(input_file, 
                                                header=0, 
                                                chunksize=self.chunk_size)]
        for _result in result_async :
            _res = _result.get()
            _graph = _graph + _res
        return _graph
        

    def processing(self): 
        """
        Search all unique objects to increase  
        """
        start_time = time.time()
        graph = self.convert_csv_to_graph(input_file=self.input_file)
        # graph = self.load_graph(input_file=self.input_file)
        # for _subject, predicate, _object in graph:
        #     print(_object)
        
        graph.serialize(destination=self.path_destination, format='turtle')
        print("--- %s seconds ---" % (time.time() - start_time))
        print('Process ended !')
        
GenerateSource(input_file='./agroLD/sameAs/valid_same_as.csv', path_destination='./agroLD/sameAs/valid_same_as.ttl', chunk_size=10000, must_augment=False).processing()
