from rdflib import Graph
from rdflib.namespace import RDF

import logging as log
from decimal import *

class CheckSimilarity: 
    """ [Check Similarity Measure]
        To confirm the similarity measure we must ensure that,
        2 predicates with high similarity  measure must have at least one common object
    """
    def __init__(self, graphs=None):
        super().__init__()
        self.graphs = graphs
        
    def get_same_objects_from_different_predicate(self, g=None, f_predicate='', s_predicate=''):
        query = """SELECT DISTINCT ?fobject
                    WHERE {
                    ?sfirst  :fpredicate  ?fobject .
                    ?ssecond :spredicate ?sobject .
                    FILTER ( ?fobject = ?sobject ).
                    }
                """
        query = query.replace(':fpredicate', f_predicate)
        query = query.replace(':spredicate', s_predicate)
        return g.query(query)


    def confirm_similarity(self, f_predicate='', s_predicate='', ):
        values = self.get_same_objects_from_different_predicate(g=self.graphs, f_predicate=f_predicate, s_predicate=s_predicate)
        for value in values : 
            if value['fobject'] :
                return True
        return False