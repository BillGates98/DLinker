from rdflib import Graph
from rdflib.namespace import RDF
from compute_files import ComputeFile
import log
from decimal import *

class Reformulation: 

    def __init__(self, input_file=''):
        self.input_file = input_file
        self.output_file = input_file.replace(input_file.split('.')[-1], 'ttl')
    
    def build_graph(self, input_file=''):
        graph = Graph()
        graph.parse(input_file)
        return graph
    
    def write_to_file(self, file_path=None,values=[]):
        with open(file_path, 'a') as f:
            f.writelines('\n'.join(values))
            f.writelines('\n')
        return None

    def run(self):
        graph = self.build_graph(input_file=self.input_file)
        output_graph = []
        for s, p, _ in graph : 
            try:
                query = "<?fsubject>  <http://www.w3.org/2002/07/owl#sameAs> <?fobject> ."
                query = query.replace('?fsubject', s)
                query = query.replace('?fobject', p)
                output_graph.append(query)
            except Exception :
                log.info('Exception during the merge process ')
        print(self.output_file)
        self.write_to_file(file_path=self.output_file, values=output_graph)
        return self.output_file
        