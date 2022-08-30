
from string_utils import StringUtils
# import spacy
import log
import validators
import numpy

# nlp = spacy.load('en_core_web_md')
	

class DeepSimilarity:
    
    def __init__(self, code=''):
        # print('Deep String Similarity')
        self.code = code
    
    def containsNumber(self, value):
        for character in value:
            if character.isdigit():
                return True
        return False

    def levenshteinDistanceDP(self, token1, token2):
        distances = numpy.zeros((len(token1) + 1, len(token2) + 1))

        for t1 in range(len(token1) + 1):
            distances[t1][0] = t1

        for t2 in range(len(token2) + 1):
            distances[0][t2] = t2
            
        a = 0
        b = 0
        c = 0
        
        for t1 in range(1, len(token1) + 1):
            for t2 in range(1, len(token2) + 1):
                if (token1[t1-1] == token2[t2-1]):
                    distances[t1][t2] = distances[t1 - 1][t2 - 1]
                else:
                    a = distances[t1][t2 - 1]
                    b = distances[t1 - 1][t2]
                    c = distances[t1 - 1][t2 - 1]
                    
                    if (a <= b and a <= c):
                        distances[t1][t2] = a + 1
                    elif (b <= a and b <= c):
                        distances[t1][t2] = b + 1
                    else:
                        distances[t1][t2] = c + 1

        # printDistances(distances, len(token1), len(token2))
        return distances[len(token1)][len(token2)]

    def measure1(self, value1='', value2=''):
        decision = False
        common_string = StringUtils().longest_substring_finder(string1=value1, string2=value2)
        # print(value1,' >>>>>>>>>>>>>>>>>>> ', value2, ' ################# ', common_string)
        _first_common_percent = len(common_string)/len(value1);
        _second_common_percent = len(common_string)/len(value2);
        if len(value1) > 1 and len(value2) > 1 :
            _nfirst_part = value1.replace(common_string, '')
            _nsecond_part = value2.replace(common_string, '')
            common_string2 = StringUtils().longest_substring_finder(string1=_nfirst_part, string2=_nsecond_part)
            if common_string2 == '' and (self.containsNumber(_nfirst_part) or self.containsNumber(_nsecond_part)):
                decision = False
            else:
                mean_score = (_first_common_percent + _second_common_percent ) / 2
                if mean_score >= 0.88 : # 0.88
                    decision = True
        # if decision : 
        #     print(value1, ' # ', value2, ' = score > ', mean_score, ' <<<>>> ', decision )
        return decision

    def measure1_(self, value1='', value2=''):
        decision = False
        common_string = StringUtils().longest_substring_finder(string1=value1, string2=value2)
        # print(value1,' >>>>>>>>>>>>>>>>>>> ', value2, ' ################# ', common_string)
        _first_common_percent = len(common_string)/len(value1);
        _second_common_percent = len(common_string)/len(value2);
        mean_score = (_first_common_percent + _second_common_percent ) / 2
        if len(value1) > 1 and len(value2) > 1 :
            _nfirst_part = value1.replace(common_string, '')
            _nsecond_part = value2.replace(common_string, '')
            common_string2 = StringUtils().longest_substring_finder(string1=_nfirst_part, string2=_nsecond_part)
            if common_string2 == '' and (self.containsNumber(_nfirst_part) or self.containsNumber(_nsecond_part)):
                decision = False
            else:
                if len(common_string2) > 0 :
                    decision = self.measure1_(value1=_nfirst_part, value2=_nsecond_part)
                else:
                    if mean_score >= 0.88 : # 0.88
                        decision = True
        # if decision : 
        #     print(value1, ' # ', value2, ' = score > ', mean_score, ' <<<>>> ', decision )
        return decision

    def measure2(self, value1='', value2=''):
        """[returns whether or not two predicate strings are similar]
        Args:
            first_value (list): [first value].
            second_value (list): [second value].
        Returns:
            [bool]: [decision on similarity or not]
        """
        decision = True
        # _first_value = StringUtils().clean_value(value=value1)
        # _second_value = StringUtils().clean_value(value=value2)
        # _nlp_first_value = nlp(_first_value)
        # _nlp_second_value = nlp(_second_value)
        # similarity_percent = _nlp_first_value.similarity(_nlp_second_value)
        # # log.info(value1 + ' => ' + value2 + '#= ' + str(similarity_percent))
        # # print('\n SCISPACY', value1,' >>>>>>>>>>>>>>>>>>> ', value2, ' ################# ', str(similarity_percent), '\n')
        # if similarity_percent >= 0.70 : 
        #     decision = True
        return decision
    
    def measure3(self, value1='', value2=''):
        """[returns whether or not two predicate strings are equal]
        Args:
            first_value (list): [first value].
            second_value (list): [second value].
        Returns:
            [bool]: [decision on similarity or not]
        """
        decision = False
        _first_value = StringUtils().clean_value(value=value1)
        _second_value = StringUtils().clean_value(value=value2)
        if self.levenshteinDistanceDP(_first_value, _second_value) <= 3 : 
            decision = True
        return decision

    def comparison_run(self, first='', second=''):
        _first_value = StringUtils().get_uri_last_part(value = first)
        _second_value = StringUtils().get_uri_last_part(value = second)
        # if validators.url(first) and validators.url(second):
        #     output = self.measure1(value1=_first_value, value2=_second_value)
        #     # print('comparison of uri')
        # else:
            # print('comparison of simple string')
        output = self.measure1_(value1=_first_value, value2=_second_value) # and self.measure2(value1=_first_value, value2=_second_value)
        return output

