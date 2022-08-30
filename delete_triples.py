from rdflib import Graph
from rdflib.namespace import RDF
from compute_files import ComputeFile
import log
from decimal import *

class DeleteTriple: 

    def __init__(self, input_path='', output_path='', predicate='owl:sameAs'):
        self.input_path = input_path
        self.output_path = output_path
        self.predicate = predicate          
    
    def delete_triples(self, graph=None, predicate=''):
        query = """SELECT DISTINCT ?fsubject ?fobject
                    WHERE {
                    ?fsubject  :fpredicate  ?fobject .
                    }
                """
        query = query.replace(':fpredicate', predicate)
        results = graph.query(query)
        for _predicate in results:
            delete_query = """
                DELETE { ?fsubject  ?predicate  ?fobject .}
                WHERE { ?fsubject  ?predicate  ?fobject. FILTER(?predicate = owl:sameAs)}
            """
            delete_query = delete_query.replace('?fpredicate', predicate)
            delete_query = delete_query.replace('?fsubject', _predicate['fsubject'])
            delete_query = delete_query.replace('?fobject', _predicate['fobject'])
            print(delete_query)
            graph.query(delete_query)
        return graph
    
    def delete_predicates(self, graph=None, predicate=''):
        query = """DELETE { ?subject  ?predicate  ?object .  }
        INSERT DATA { ?subject  owl:none  ?object }
            WHERE   { 
                ?subject  ?predicate  ?object .
            }"""
        query = query.replace('?predicate', predicate)
        graph.query(query)
        return graph
    
    def load_graph(self, input_file=''):
        """
            expands the data and puts the new version in the associated output file
        """
        graph=Graph()
        try:
            graph.parse(input_file)
        except Exception as _ :
            log.critical('#Not converted to graph >> ' + input_file + ' ....%')
        return graph

    def run(self):
        inputs, outputs = ComputeFile(input_path=self.input_path, output_path=self.output_path).build_list_files_without_graphs()
        for i in range(len(inputs)) :
            graph = self.load_graph(input_file=inputs[i])
            graph = self.delete_triples(graph=graph, predicate=self.predicate)
            try:
                graph.serialize(destination=outputs[i], format='turtle')
            except Exception :
                log.info('Exception during the merge process ')
        return

DeleteTriple(input_path='./inputs/', output_path='./cleaned_data/').run()
        