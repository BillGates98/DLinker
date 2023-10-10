
from string_utils import StringUtils
# import spacy
import log
import validators
import numpy as np
from dump import dump

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
    
    def ngram_similarity(self, value1='', value2='', N=3):
        def extract_ngrams(s, n):
            ngrams = []
            for i in range(len(s) - n + 1):
                ngram = s[i:i + n]
                ngrams.append(ngram)
            return ngrams

        ngrams1 = extract_ngrams(value1, N)
        ngrams2 = extract_ngrams(value2, N)

        common_ngrams = set(ngrams1) & set(ngrams2)
        similarity = len(common_ngrams) / max(max(len(ngrams1), len(ngrams2)), 1)
        # similarity2 = len(common_ngrams) / (min(len(ngrams1), len(ngrams2)) - N + 1)
        return True if similarity >= 0.8 else False
    
    def jaro_similarity(self, value1='', value2=''):
        def jaro_winkler_distance(s1, s2):
            len_s1 = len(s1)
            len_s2 = len(s2)

            max_len = max(len_s1, len_s2)

            match_distance = (max_len // 2) - 1

            s1_matches = [False] * len_s1
            s2_matches = [False] * len_s2

            matches = 0

            for i in range(len_s1):
                start = max(0, i - match_distance)
                end = min(i + match_distance + 1, len_s2)

                for j in range(start, end):
                    if not s2_matches[j] and s1[i] == s2[j]:
                        s1_matches[i] = True
                        s2_matches[j] = True
                        matches += 1
                        break

            if matches == 0:
                return 0.0

            transpositions = 0
            k = 0
            for i in range(len_s1):
                if s1_matches[i]:
                    while not s2_matches[k]:
                        k += 1
                    if s1[i] != s2[k]:
                        transpositions += 1
                    k += 1

            jaro_similarity = (matches / len_s1 + matches / len_s2 + (matches - transpositions / 2) / matches) / 3.0

            return jaro_similarity

        jaro_distance = jaro_winkler_distance(value1, value2) # 1.0 - 
        # print('\t jaro : ', jaro_distance)
        return jaro_distance
    
    def substringsim(self, value1='', value2=''):
        common_string = StringUtils().longest_substring_finder(string1=value1, string2=value2)
        val_len1 = len(value1)
        val_len2 =  len(value2)
        score = 0.0
        if len(value1) > 1 and len(value2) > 1 :
            score = 2 * len(common_string) / (val_len1 + val_len2)
        return score

    def measure1_(self, value1='', value2='', alpha=0, level=1):
        decision = False
        val_len1 = len(value1)
        val_len2 = len(value2)
        # ratio  = val_len1/val_len2
        if val_len1 > 1 and val_len2 > 1 : # and ratio < 1:
            common_string = StringUtils().longest_substring_finder(string1=value1, string2=value2)
            score = 2 * len(common_string) / (val_len1 + val_len2)
            # _first_common_percent = len(common_string)/val_len1
            # _second_common_percent = len(common_string)/val_len2
            # mean_score = (_first_common_percent + _second_common_percent ) / 2

            if (score >= alpha) :
                decision = True
            else:
                _nfirst_part = value1.replace(common_string, '')
                _nsecond_part = value2.replace(common_string, '')    
                common_string2 = StringUtils().longest_substring_finder(string1=_nfirst_part, string2=_nsecond_part)
                if common_string2 == '' and (self.containsNumber(_nfirst_part) or self.containsNumber(_nsecond_part)):
                    decision = False
                else:
                    if len(common_string2) > 0 and level > 0 :
                        decision = self.measure1_(value1=_nfirst_part, value2=_nsecond_part, alpha=alpha, level=level-1)                   
        return decision

    def hamming(self, value1='', value2=''):
        _lvalue1 = len(value1)
        _lvalue2 = len(value2)
        sim = 0
        for i in range(min(_lvalue1, _lvalue2)):
            sim += 1 if value1[i] == value2[i] else 0
        final = (sim + abs(_lvalue1 - _lvalue2) ) / max(_lvalue1, _lvalue2)
        return final

    def comparison_run(self, first='', second='', alpha=0, level=0):
        _first_value = StringUtils().get_uri_last_part(value = first)
        _second_value = StringUtils().get_uri_last_part(value = second)
        # output0 = self.measure1_(value1=_first_value, value2=_second_value, alpha=alpha, level=level) 
        # print('\n Comparison : ', _first_value, ' And ' , _second_value )
        _, output1 = self._substringsim(value1=_first_value, value2=_second_value) 
        # output3 = self.hamming(value1=_first_value, value2=_second_value) 
        # output2 = self.jaro_similarity(value1=_first_value, value2=_second_value) 
        # vals = [output1, output2, output3] 
        if output1 >= alpha :
            # print(output1)
            # print(output3, ' => ', output2, ' => ', abs(output3-output2))
            return True
        # print('lcs : ', output1, ' hamming : ', output2, ' jaro similarity : ', output3)
        return False # output2 and output3
    
    ##
    ##
    ##

    def _substringsim(self, value1='', value2=''):
        common_string = StringUtils().longest_substring_finder(string1=value1, string2=value2)
        val_len1 = len(value1)
        val_len2 =  len(value2)
        score = 2 * len(common_string) / (val_len1 + val_len2)
        # print('Score : ', score)
        # print('c : ', len(common_string), ' l1 : ', val_len1, ' l2 : ', val_len2)
        return common_string, score
    
    def _hamming(self, value1='', value2=''):
        _lvalue1 = len(value1)
        _lvalue2 = len(value2)
        sim = 0
        for i in range(min(_lvalue1, _lvalue2)):
            sim += 1 if value1[i] == value2[i] else 0
        final = (sim + abs(_lvalue1 - _lvalue2) ) / max(_lvalue1, _lvalue2)
        return final
    
    def _comparison(self, first='', second='', alpha=0):
        _first_value = StringUtils().get_uri_last_part(value = first)
        _second_value = StringUtils().get_uri_last_part(value = second)
        output1 = self._substringsim(value1=_first_value, value2=_second_value) 
        # output2 = self._hamming(value1=_first_value, value2=_second_value) 
        return output1 #, output2)

