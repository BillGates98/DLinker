import json
import log
from rdflib import Graph
from deep_similarity import DeepSimilarity
import numpy as np
import random
import validators
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import OWL

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from rdflib import Graph, URIRef, Literal
import networkx as nx
from node2vec import Node2Vec
from collections import Counter
from tqdm import tqdm 
import time
import re
from pyjarowinkler import distance
import string
import multiprocessing
import itertools

# import nltk
# from nltk.corpus import stopwords
# nltk.download('stopwords') 



start_time = time.time()

output_files = [
    './outputs/anatomy/tmp_same_as.ttl',
    './outputs/doremus/tmp_same_as.ttl',
    './outputs/agrold/tmp_same_as.ttl',
    './outputs/SPIMBENCH_small-2016/tmp_same_as.ttl',
    './outputs/spaten_hobbit/tmp_same_as.ttl'
]
truth_files = [
    './validations/anatomy/valid_same_as.ttl',
    './validations/doremus/valid_same_as.ttl',
    './validations/agrold/valid_same_as.ttl',
    './validations/SPIMBENCH_small-2016/valid_same_as.ttl',
    './validations/spaten_hobbit/valid_same_as.ttl'
]

index = 1
output_file = output_files[index]
truth_file = truth_files[index]



vocabulary = dict()
synonyms = dict()

word_counts = Counter()

ds = DeepSimilarity(code='*')

output_alignements = {}

def sigmoid(value):
    return 1 / (1 + np.exp(-value))

def sim(entity1=[], entity2=[]):
    jaros = []
    for p1, o1 in entity1:
        if not validators.url(o1) :
            for p2, o2 in entity2:
                if not validators.url(o2) :
                    jaro_sim = round(ds.jaro_similarity(value1=o1, value2=o2), 2)
                    if jaro_sim > 0:
                        jaros.append(jaro_sim)
    if len(jaros) > 0 :
        decision = np.mean(np.array(jaros))
        if decision >= 0.3 :
            return True
    return False
    
def clean_sentence(sentence):
    cleaned_sentence = ''.join(char for char in sentence if char not in string.punctuation)
    return cleaned_sentence.lower()

def calculate_alignment_metrics(output_file, truth_file):
    output_graph = Graph()
    output_graph.parse(output_file, format="turtle")

    truth_graph = Graph()
    truth_graph.parse(truth_file, format="turtle")

    found_alignments = set(output_graph.subjects())
    true_alignments = set(truth_graph.subjects())
    print('Count of true alignments : ', len(true_alignments))
    intersection = len(found_alignments.intersection(true_alignments))
    precision = intersection / len(found_alignments) if len(found_alignments) > 0 else 0.0
    recall = intersection / len(true_alignments) if len(true_alignments) > 0 else 0.0
    f_measure = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f_measure": f_measure
    }

def create_and_save_rdf_from_dict(input_dict, output_file):
    graph = Graph()
    # owl = Namespace("http://www.w3.org/2002/07/owl#")
    for source, target in input_dict.items():
        source_uri = URIRef(source)
        target_uri = URIRef(target)
        graph.add((source_uri, OWL.sameAs, target_uri))
    graph.serialize(destination=output_file, format="turtle")

def get_rdf_objects(rdf_graph):
    objects = list(rdf_graph.objects())
    return objects

def valeur_minimum_frequence(liste):
    frequence = Counter(liste)
    min_frequence = min(frequence.values())
    valeurs_min_frequent = [element for element, freq in frequence.items() if freq >= min_frequence]
    return valeurs_min_frequent

def get_rdf_triples(rdf_graph):
    output = {}
    objects = {}
    for s, p, o in tqdm(rdf_graph):
        s = str(s)
        p = str(p)
        o = str(o)
        if not s in output :
            output[s] = []
        
        if not o in objects :
            objects[o] = 0

        objects[o] += 1
        output[s].append((p, o))    
    return output, objects

def predicate_objects(objects1={}, objects2={}):
    output = {}
    min1 = min(valeur_minimum_frequence(list(objects1.values())))
    min2 = min(valeur_minimum_frequence(list(objects2.values())))
    gmin = min(min1, min2)
    for obj in tqdm(objects1) :
        if obj in objects2 :
            a = objects1[obj]
            b = objects2[obj] 
            _min = min(a, b)
            prob = _min / max(a,b)
            if _min >= gmin and prob >= 0.5 : #  
                output[obj] = {'s': objects1[obj], 't': objects2[obj], 'probability': prob}
    return  output

def reduce_entities(subjects, candidatures, entry='s'):
    tmp = {}
    output = {}
    assoc = {'s': 't', 't': 's'}
    sums = []
    for s in tqdm(subjects):
        _triples = subjects[s]
        _sum = 0.0
        for p , o in _triples :
            if o in candidatures :
                _sum = _sum + ( (1/candidatures[o][entry]) * candidatures[o][assoc[entry]] )
                sums.append(round(_sum,0))
                tmp[s] = _sum
    # v = int(np.mean(valeur_minimum_frequence(sums)))
    v = int(np.mean(sums))
    print(' v : ', v )
    # if v < 4 :
    #     _randed = random.choices(list(tmp.keys()), k=4500)
    #     for s in _randed :
    #         output[s] = subjects[s]
    # else : 
    for s in tmp:
        _sum = tmp[s]
        if _sum > 4 : # critic # agroLD 2 # doremus 4 # spim : 11
            output[s] = subjects[s]
    # print(output)
    return output

def random_selections(data=[], k=0):
    _randed = random.choices(data, k=k)
    return _randed


# End of embedding functions
#

def parallel_running(sub1, sub2, subs1, subs2):
    if sim(entity1=subs1[sub1], entity2=subs2[sub2]):
        return sub1, sub2
    return None, None

def random_selection(data1=[], data2=[], k=0.1):
    pairs = []
    print('Pairs selection ... ', int(len(data1)*k))

    tmp = [i for i in range(len(data1))]
    for entity2 in data2:
        for _ in range(int(len(data1)*k)):
            entity1 = data1[random.choice(tmp)]
            pairs.append((entity1, entity2))
    return pairs

def process_rdf_files(file1, file2):
    
    graph1 = Graph()
    graph1.parse(file1)
    print('Source file loaded ..100%')
    graph2 = Graph()
    graph2.parse(file2)  
    print('Target file loaded ..100%')

    graph3 = Graph()
    graph3.parse(truth_file)  
    print('Truth file loaded ..100%')

    print('Graph1 Subjects\'s and Objects\' list are building ..0%')
    subjects1, objects1 = get_rdf_triples(graph1)
    print('Graph2 Subjects\'s and Objects\' list are building ..0%')
    subjects2, objects2 = get_rdf_triples(graph2)
    print('Building ended')

    print(' Candidatures building')
    candidatures = predicate_objects(objects1, objects2)
    # print(candidatures)
    # exit()
    print('Candidates reducing ')
    print( len(list(subjects1.keys())) )
    print( len(list(subjects2.keys())) )
    subjects1 = reduce_entities(subjects1, candidatures, entry='s')
    subjects2 = reduce_entities(subjects2, candidatures, entry='t')
    print( len(list(subjects1.keys())) )
    print( len(list(subjects2.keys())) )
    # exit
    # for s, _, t in graph3:
    #     if sim(entity1=subjects1[str(s)], entity2=subjects2[str(t)]):
    #         output_alignements[str(s)] = str(t)
    exit()
    pairs = random_selection(data1=list(subjects1.keys()), data2=list(subjects2.keys()), k=1.0) # important agroLD : 0.001
    print(f'{len(pairs)} pairs ')
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.starmap(parallel_running, [ (sub1, sub2, subjects1, subjects2) for sub1, sub2 in tqdm(pairs)] )
        # print(results)
        for sub1, sub2 in results :
            if sub1 != None and sub2 != None :
                output_alignements[sub1] = sub2

    print(f' \nThey are {len(list(output_alignements.keys()))} in all')
    create_and_save_rdf_from_dict(output_alignements, output_file)
    metrics = calculate_alignment_metrics(output_file, truth_file)
    print("Precision : ", metrics["precision"])
    print("Recall : ", metrics["recall"])
    print("F-measure : ", metrics["f_measure"])

    end_time = time.time()
    execution_time = end_time - start_time
    print(f" \n Running time : {execution_time} seconds")

if __name__ == "__main__":

    files1 = [
        './inputs/anatomy/source.owl',
        './inputs/doremus/source.ttl',
        './inputs/agrold/source.nt',
        './inputs/SPIMBENCH_small-2016/source.nt',
        './inputs/spaten_hobbit/source.nt'
    ]

    files2 = [
        './inputs/anatomy/target.owl',
        './inputs/doremus/source.ttl',
        './inputs/agrold/target.nt',
        './inputs/SPIMBENCH_small-2016/target.nt',
        './inputs/spaten_hobbit/target.nt'
    ]

    file1 = files1[index]
    file2 = files2[index]
    process_rdf_files(file1, file2)
