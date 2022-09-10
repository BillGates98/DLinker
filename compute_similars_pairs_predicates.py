import json
import re
import string
from xmlrpc.client import boolean

from dump import dump
from check_similarity import CheckSimilarity
import spacy
import log
nlp = spacy.load('en_core_web_md')

class ComputeSimilarPredicate:
    def __init__(self, predicates=[], graphs=None, alpha_predicate=1, output_path=''):
        self.predicates = predicates
        self.path_to_file = './outputs/outputs.json'
        self.graphs = graphs
        self.associated_predicates = {}
        self.alpha_predicate = alpha_predicate
        self.output_path = output_path
        log.info('Compute similars predicates')
    
    def get_initial_predicate_with_uri(self, value=''):
        """[returns the uri associated with the suffix of 'prefix:suffix']
        Args:
            value (str): [in the form 'prefix:suffix'].
        Returns:
            [str]: [the uri associated with 'prefix:suffix']
        """
        for _uri, suffix in self.predicates :
            if suffix == value :
                return _uri
        return None

    def get_initial_raw_predicate(self, value=''):
        """[returns the uri associated with the suffix of 'prefix:suffix']

        Args:
            value (str): [in the form 'prefix:suffix'].

        Returns:
            [str]: [the uri associated]
        """
        assoc_predicates = self.associated_predicates
        for suffix in assoc_predicates :
            if assoc_predicates[suffix] == value :
                return self.get_initial_predicate_with_uri(value=suffix)
        return None
    
    def build_pairs(self, predicates=[]):
        """[returns the predicate pairs to compare]

        Args:
            predicates (list): [a list of predicate arrays].

        Returns:
            [array]: [a list of pairs formed]
        """
        outputs = []
        for first in range(len(predicates)) :
            for second in range(first, len(predicates)) :
                if first != second : 
                    outputs.append((predicates[first], predicates[second]))
        return outputs

    def clean_value(self, value=''):
        """[returns a syntactically and easily comparable sentence]

        Args:
            value (str): [string with special characters].

        Returns:
            [type]: [string without special characters]
        """
        chars = re.escape(string.punctuation)
        _value = re.sub(r'['+chars+']', ' ', value)
        _value = re.sub(r"(\w)([A-Z])", r"\1 \2", _value)
        # track initial value to last value
        self.associated_predicates[value] = _value
        return _value.lower()
    
    def compute_similar_values(self, first_value='', second_value=''):
        """[returns whether or not two predicate strings are similar]

        Args:
            first_value (list): [first value].
            second_value (list): [second value].

        Returns:
            [bool]: [decision on similarity or not]
        """
        decision = False
        _first_value = self.clean_value(value=first_value)
        _second_value = self.clean_value(value=second_value)
        
        _nlp_first_value = nlp(_first_value)
        _nlp_second_value = nlp(_second_value)
        similarity_percent = _nlp_first_value.similarity(_nlp_second_value)
        # print(first_value + ' => ' + second_value + '#= ' + str(similarity_percent))
        if similarity_percent >= self.alpha_predicate : 
            decision = True
            log.info(first_value + ' => ' + second_value + '#= ' + str(similarity_percent))
        
        return decision, similarity_percent
    
    def compute_predicate_similarity(self, first_predicates=[], second_predicates=[]):
        """[returns a set of predicates and its similar predicates]

        Args:
            first_predicates (list): [first set of predicates].
            second_predicates (list): [second set of predicates].

        Returns:
            [dict]: [dictionary of predicates and their similar predicates]
        """
        result = {}
        fupredicates = []
        fupredicates_v = []
        supredicates = []
        supredicates_v = []
        similarities = []
        values = {}
        for f_uri_predicate, first_value in first_predicates:
            for s_uri_predicate, second_value in second_predicates:
                tmp_similarity, similarity_percent = self.compute_similar_values(first_value=first_value, second_value=second_value)
                if tmp_similarity :
                    # print('>>>>>>>>>> ', f_uri_predicate, ' # ', s_uri_predicate, ' ==> ', tmp_similarity)
                    fupredicates.append(f_uri_predicate)
                    fupredicates_v.append(first_value)
                    supredicates.append(s_uri_predicate)
                    supredicates_v.append(second_value)
                    similarities.append(similarity_percent)
                    #
        values['predicate_1'] = fupredicates
        values['value_1'] = fupredicates_v
        values['predicate_2'] = supredicates
        values['value_2'] = supredicates_v
        values['similarities'] = similarities
        dump().write_to_csv_panda(file_name=self.output_path + 'similars_predicates', data=values)
        return result
    
    def run(self):
        set_predicates = self.build_pairs(predicates=self.predicates)
        all_couples = []
        for first, second in set_predicates :
            all_couples.append(self.compute_predicate_similarity(first_predicates=first, second_predicates=second))
        
                   
