from rdflib import Graph, Literal
from rdflib.namespace import RDF

import log
from decimal import *

class HandlePredicates: 

    def __init__(self, input_files=[], graphs=[]):
        super().__init__()
        self.input_files = input_files
        self.grapĥs = graphs
        self.dataset_predicates = []
        
    def get_suffix(self, value='', prefixes=[]):
        for prefix in prefixes:
            if prefix in value :
                return value.replace(prefix, '')
        return value   
    
    def get_predicate_type(self, graph=None, predicate=''):
        query = """SELECT DISTINCT ?o WHERE { ?s ?p ?o .} LIMIT 1""".replace('?p', '<' + predicate + '>')
        for _object in graph.query(query):
            if isinstance(_object['o'], Literal):
                return 'literal'
        return ''
    
    def get_predicates(self, graph=None):
        query = """SELECT DISTINCT ?p WHERE { ?s ?p ?o .}"""
        return graph.query(query)
    
    def extract_predicates(self, graph=None):
        predicates = []
        namespaces = graph.namespace_manager.namespaces()
        prefixs_values = []
        for _, url in namespaces :
            prefixs_values.append(str(url)) # url.n3()
        
        for _predicate in self.get_predicates(graph=graph):
            tmp_predicate = _predicate['p']
            if self.get_predicate_type(graph=graph, predicate=tmp_predicate) == 'literal':
                predicates.append((tmp_predicate.n3(), self.get_suffix(value=tmp_predicate, prefixes=prefixs_values)))
        # predicates = list(dict.fromkeys(predicates))
        self.dataset_predicates.append(predicates)
        return graph

    def run(self):
        graphs = self.grapĥs   
        for i in range(len(graphs)) :
            log.critical('#Started on the file ' + self.input_files[i]+ '-> ...%')
            self.extract_predicates(graph=graphs[i])
        return self.dataset_predicates
        