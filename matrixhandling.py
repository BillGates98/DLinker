from statistics import mean
import numpy as np
from collections import Counter
import math
from dump import dump

class MatrixHandling:
    
    def __init__(self, ptensors=[], ltensors=[], predicates_couples=[], output_path=''):
        # print('Matrix handling')
        self.ptensors = ptensors
        self.ltensors = ltensors
        self.predicates_couples = predicates_couples
        self.output_path = output_path
    
    """_summary_ : find hyperparameter locally
    """
    def predicate_ceil(self, matrix=[]):
        _matrix = np.matrix(matrix)
        _max = np.argmax(_matrix)
        return _matrix.item(_max)
    
    def proportion_of_value(self, tab=[]):
        prop = 0
        for x in tab:
            if x == 0.0 :
                prop = prop + 1
        if prop/len(tab) <= 0.5 :
            return True
        return False
    
    def literal_ceil(self, matrix=[]):
        int_matrix = []
        good_predicates = []
        for index in range(len(matrix)):  
            if self.proportion_of_value(tab=matrix[index]) :
                int_matrix.append(matrix[index])
                fs, ss = self.predicates_couples[index%len(self.predicates_couples)]
                good_predicates.append((fs, ss))
        if (len(int_matrix)>0) :
            _matrix = np.matrix(int_matrix)
            _means_r = _matrix.mean(0)
            _means_c = _matrix.mean(1)
            _max_r = _means_r.item(np.argmax(_means_r))
            _max_c = _means_c.item(np.argmax(_means_c))
            return max(_max_r, _max_c), good_predicates
        return None, None

    
    def most_commun(self, tab=[]):
        a = Counter(tab)
        mc = a.most_common(1)
        if len(mc) > 0 :
            mc = mc[0][1]
        return mc
    
    def threshold_acceptance(self, matrix=[]):
        _matrix = np.matrix(matrix)
        _means_r = _matrix.mean(0)
        _means_c = _matrix.mean(1)
        tmpr = [_means_r.item(i) for i in range(_means_r.size)]
        tmpc = [_means_c.item(i) for i in range(_means_c.size)]
        return min(self.most_commun(tab=tmpc), self.most_commun(tab=tmpr))

    def depth_ceil(self, matrix=[]):
        _matrix = np.matrix(matrix)
        _means = _matrix.mean(0)
        output = 0
        tmp_means = [ _means.item(i) for i in range(_means.size)]
        max_mean = max([ _means.item(i) for i in range(_means.size)])
        if _means.size > 0 :
            a = np.array(tmp_means)
            output = a.tolist().index(max_mean)
        return output
    
    def _local_yield_(self, datas=[]):
        output = {
            'ceil_p': [],
            'ceil_o': [],
            'threshold_acceptance': [],
            'depth_p': [],
            'depth_o': [],
        }
        good_predicates = []
        for i in range(len(datas)): 
            if len(self.ltensors[i]) > 0 and len(self.ptensors[i]) > 0 :
                # print(self.ltensors[i])
                # print('----')
                # print(self.ptensors[i])
                cp = self.predicate_ceil(matrix=self.ptensors[i])
                co, good_predicate = self.literal_ceil(matrix=self.ltensors[i])
                # print(list(set(good_predicate)))
                if co != None :
                    good_predicates = good_predicates + good_predicate
                    output['ceil_p'].append(cp)
                    output['ceil_o'].append(co)
                    output['threshold_acceptance'].append(self.threshold_acceptance(matrix=self.ptensors[i]))
                    output['depth_o'].append(self.depth_ceil(matrix=self.ltensors[i]))
                    output['depth_p'].append(self.depth_ceil(matrix=self.ptensors[i]))
        return output, list(set(good_predicates))
    
    """_summary_ : find hyperparameter globally
    """
    def _global_yield_(self, output={}):
        _output = {}
        for key in output:
            if key == 'ceil_o' :
                frac, _ = math.modf(sum(output[key]))
                _output[key] = frac
            else:
                _output[key] = mean(output[key])
        _output['threshold_acceptance'] = math.ceil(_output['threshold_acceptance'])
        _output['depth_o'] = math.ceil(_output['depth_o'])
        return _output
    
    def save_predicates_to_csv(self, data=[]):
        values = {}
        fupredicates = []
        fupredicates_v = []
        supredicates = []
        supredicates_v = []
        similarities = []
        for fs, ss in data :
            fupredicates.append('<' + fs + '>')
            fupredicates_v.append(fs.split('/')[-1])
            supredicates.append('<' + ss + '>')
            supredicates_v.append(ss.split('/')[-1])
            similarities.append('G')
        values['predicate_1'] = fupredicates
        values['value_1'] = fupredicates_v
        values['predicate_2'] = supredicates
        values['value_2'] = supredicates_v
        values['similarities'] = similarities
        dump().write_to_csv_panda(file_name=self.output_path.replace('inputs','outputs') + '/similars_predicates', data=values)
        return None
    
    def run(self):
        output, good_predicates = self._local_yield_(datas=self.ptensors)
        _output = self._global_yield_(output=output)
        self.save_predicates_to_csv(data=good_predicates)
        return self.output_path.split('/')[-1], _output, list(set(good_predicates))