from html import entities
import xmltodict
from rdflib import Graph
from  compute_files import ComputeFile
from itertools import combinations
from itertools import product
import multiprocessing

class Convertor:
    
    def __init__(self, input_path='', input_file='', destination=''):
        print('Convertor')
        self.xml = None
        self.destination = destination
        self.input_path = input_path
        with open(input_file) as xmlfile:
            self.xml = xmltodict.parse(xmlfile.read())
    
    def cartesian_product(self, set1=[], set2=[]):
        return list(product(set1, set2))
    
    def important_part(self, _value=''):
        output = ''
        split = _value.split('/')
        if len(split) == 5 :
            output = _value
        else:
            if len(split) > 5 :
                remain = len(split) - 5
                output = '/'.join(split[:-1*remain])
        return output
    
    def get_entities(self, graph=None, entities=[], dsource=''):
        query = """SELECT DISTINCT ?s WHERE { ?s ?p ?o .}"""
        results = graph.query(query)
        outputs = []
        
        for _subject in results:
            value = self.important_part(_value=_subject['s'])
            if value.startswith('http') and (value in entities):
                outputs.append(_subject['s'])
                print( value, ' ===> ', (value in entities) )
        return outputs
    
    def split_arrays(self, a = [], n=16):
        k, m = divmod(len(a), n)
        return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    def find_valid_pairs(self, pairs=[], entities1=[], entities2=[]):
        outputs = []
        for entity1, entity2 in pairs:
            _ivalue_entity1 = self.important_part(_value=entity1)
            _ivalue_entity2 = self.important_part(_value=entity2)
            
            _index_ivalue_entity1 = entities1.index(_ivalue_entity1)
            _index_ivalue_entity2 = entities2.index(_ivalue_entity2)
            if _index_ivalue_entity1 == _index_ivalue_entity2 :
                outputs.append((entity1, entity2))        
                outputs.append((_ivalue_entity1, _ivalue_entity2))        
        return outputs 
    
    def get_pairs_entites(self, graph_source=None, entities1=[], graph_target=None, entities2=[]):
        outputs = []
        outputs_entities1 = self.get_entities(graph=graph_source, entities=entities1, dsource='source')
        outputs_entities2 = self.get_entities(graph=graph_target, entities=entities2, dsource='target')
        outputs_products = self.cartesian_product(set1=outputs_entities1, set2=outputs_entities2)
        # parallel computing
        pool = multiprocessing.Pool()
        result_async = [pool.apply_async(self.find_valid_pairs, args =(chunked_data, entities1, entities2, )) for chunked_data in self.split_arrays(a=outputs_products)]
        for _result in result_async :
            _res = _result.get()
            outputs = outputs + _res
        print('get_pairs_entites')
        return outputs
             
    def convert(self):
        count = 0
        output = []
        for map in self.xml["rdf:RDF"]["Alignment"]["map"]:
            if map :
                entity1 = map['Cell']['entity1']['@rdf:resource']
                entity2 = map['Cell']['entity2']['@rdf:resource']
                # print(entity1, ' owl:sameAs ', entity2)
                output.append((entity1, entity2))
                count = count + 1
        print('Count :', count)
        return output

    def save_entityies_to_graph(self, alignments=[], file_name=''):
        graph = Graph()
        _predicate = 'http://www.w3.org/2002/07/owl#sameAs'
        for entity1, entity2 in alignments :
            query = """INSERT DATA { <?subject>  <?predicate>  <?object> . }"""
            query = query.replace('?subject', entity1).replace('?predicate',  _predicate).replace('?object',  entity2)
            query_result = None
            try:
                query_result = graph.update(query)
                if query_result != None :
                    continue
            except Exception as _:
                continue
        graph.serialize(destination=self.destination + file_name + '.ttl', format='turtle')
        return graph
    
    def run(self):
        pattern_matching = self.convert()
        self.save_entityies_to_graph(alignments=pattern_matching, file_name='valid_same_as')
        # _, _, graphs = ComputeFile(input_path=self.input_path, output_path='./outputs/').build_list_files()
        # alignments = self.get_pairs_entites(graph_source=graphs[0], graph_target=graphs[1])
        # self.save_entityies_to_graph(alignments=alignments, file_name='valid_same_as')
        
Convertor(input_path='./inputs/', input_file='./conversions/data.xml', destination='./conversions/').run()