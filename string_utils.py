
import validators
import re
import string

class StringUtils:
    
    def __init__(self):
        pass
    
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
        return _value.lower()
    
    def get_uri_last_part(self, value=''):
        output = value
        if len(value) > 0 :
            output = ' '.join(value.lower().split())
        # if validators.url(value) :
        #     return value.rsplit('/', 1)[-1]
        return output.lstrip()

    def longest_substring_finder(self, string1='', string2=''):
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            for j in range(len2):
                lcs_temp=0
                match=''
                while ((i+lcs_temp < len1) and (j+lcs_temp<len2) and string1[i+lcs_temp] == string2[j+lcs_temp]):
                    match += string2[j+lcs_temp]
                    lcs_temp+=1
                if (len(match) > len(answer)):
                    answer = match
        return answer