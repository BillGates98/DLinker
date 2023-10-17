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
# output_file = './outputs/doremus/tmp_same_as.ttl'
# truth_file = './validations/doremus/valid_same_as.ttl'

# output_file = './outputs/agrold/tmp_same_as.ttl'
# truth_file = './validations/agrold/valid_same_as.ttl'

# output_file = './outputs/anatomy/tmp_same_as.ttl'
# truth_file = './validations/anatomy/valid_same_as.ttl'

output_file = './outputs/SPIMBENCH_small-2016/tmp_same_as.ttl'
truth_file = './validations/SPIMBENCH_small-2016/valid_same_as.ttl'

# output_file = './outputs/spaten_hobbit/tmp_same_as.ttl'
# truth_file = './validations/spaten_hobbit/valid_same_as.ttl'


probabilities = {}

vocabulary = dict()
synonyms = dict()

word_counts = Counter()

ds = DeepSimilarity(code='*')

output_alignements = {}

def sigmoid(value):
    return 1 / (1 + np.exp(value))

def hamming(v1=[], v2=[]):
    counter = 0
    for i in range(len(v1)):
        if v1[i] != 0.0 and v2[i] != 0.0 and v1[i] != v2[i] :
            counter = counter + 1
    return counter

def pearson(v1=[], v2=[]):
    mean1 = np.mean(v1)
    mean2 = np.mean(v2)

    n1s = 0.0
    d1s = 0.0
    d2s = 0.0
    for i in range(len(v1)):
        n1 = v1[i] - mean1
        n2 = v2[i] - mean2
        n1s = n1s + (n1 * n2)
        d1s = d1s + n1**2
        d2s = d2s + n2**2
    r = n1s / (d1s * d2s)
    return r

def minkowski(v1=[], v2=[]):
    return np.sum(np.absolute(v1-v2))


def checking(v1=[], v2=[]):
    v = v1 - v2
    notnulls = 1
    sim = 0
    dsim = 0
    for i in range(len(v)):
        if v1[i] != 0.0 and v2[i] != 0.0 and v[i] == 0.0 :
            sim += 1

        elif (v1[i] != 0.0 and v2[i] != 0.0 and v[i] != 0.0) :
            dsim += 1
        
        if v1[i] != 0.0 and v2[i] != 0.0 :
            notnulls += 1 
    notnulls = notnulls - 1 if notnulls > 1 else notnulls 
    dot = np.dot(v1, v2)
    diff = dot/np.linalg.norm(np.absolute(v1-v2))
    return dot, diff, sim, dsim, notnulls

def cosine_sim(v1=[], v2=[]):
    output = 0.0
    dot = np.dot(v1, v2)
    # diff = dot/np.linalg.norm(np.absolute(v1-v2))
    if dot > 0.0 :
        de1 = np.linalg.norm(v1)
        de2 = np.linalg.norm(v2)
        cosine = dot / (  de1*de2 )
        # output = round(cosine - (cosine*(dsim/notnulls)), 2)
        ham = hamming(v1, v2)
        pears = pearson(v1, v2)
        output = round(cosine*pears*dot, 2)
        if output >= 0.5 :
            print('Dot : ', dot, ' Cosine : ', output, ' hamming : ', ham, ' pearson : ', pears) # , ' minkowski : ', minkowski(v1, v2))
            return True
    return False


def find_similar_word(target_word, dictionary, threshold=0.9):
    similar_words = []

    if target_word in dictionary:
        return 1
    
    for word in dictionary:
            word = clean_sentence(word)
            jaro_similarity = round(ds.jaro_similarity(value1=word, value2=target_word), 2)
            
            if jaro_similarity >= threshold:
                similar_words.append((word, jaro_similarity))
    if not similar_words:
        vocabulary[target_word] = len(list(vocabulary.keys()))
        return 1
    else:
        similar_words.sort(key=lambda x: x[1], reverse=True)
        if not target_word in similar_words :
            synonyms[target_word] = []
        for sw in similar_words :
            synonyms[target_word].append(sw)
    return 1

def find_similar_words(vocabulary, objects):
    print('Find synonyms ...%')
    visited = []
    for obj in tqdm(objects):
        _o = str(obj)
        if not validators.url(_o):
            _o = remove_stopwords(_o)
            for _oo in _o.split():
                if not _oo.strip() in visited and not validators.url(_oo):
                    _oo = clean_sentence(_oo)
                    find_similar_word(_oo, random.choices(list(vocabulary.keys()), k=500))
                    visited.append(_oo)
    
def clean_sentence(sentence):
    # Remove punctuation and special characters : string.punctuation
    cleaned_sentence = ''.join(char for char in sentence if char not in string.punctuation)
    return cleaned_sentence.lower()

def remove_stopwords(input_text, language='english'):
    # stop_words = set(stopwords.words(language))
    # words = input_text.split() 
    # cleaned_words = [word for word in words if word.lower() not in stop_words]
    return input_text


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

#
# Embedding section
#
def extract_words_from_objects(object_list):
    for obj in object_list:
        _obj = str(obj)
        if not validators.url(_obj):
            _obj = remove_stopwords(_obj)
            words = [ clean_sentence(v) for v in  _obj.split() ]
            word_counts.update(words)
            for word in words:
                if not word in vocabulary :
                    vocabulary[word] = len(vocabulary)
    return vocabulary

def get_rdf_objects(rdf_graph):
    objects = list(rdf_graph.objects())
    return objects

def word_to_binary_vector(word):
    binary_vector = [0.0] * (len(vocabulary)+1)
    wc = dict(word_counts)
    _word_in_voc = word
    # print(word, ' # ' , len(synonyms.keys()), ' synonyms ')
    if word in synonyms :
        # print(word, ' in syns and not in voc >> ', synonyms[word][0][0])
        _word_in_voc = synonyms[word][0][0]

    if _word_in_voc in vocabulary:
        word_index = vocabulary[_word_in_voc]
        # print('\t length : ', word_index, ' / ', len(vocabulary))
        binary_vector[word_index] = 1.0 # / wc[word]
    return binary_vector

def sentence_to_vector(sentence):
    _vector = np.array([0.0] * (len(vocabulary)+1))    
    for word in sentence.split():
        if not validators.url(word) :
            word = clean_sentence(word)
            _vector = _vector + np.array(word_to_binary_vector(word))
    return _vector

def graph_to_vect(graph):
    subjects = {}
    _len_voc = len(vocabulary) + 1
    for _s, _, _o in tqdm(graph):
        s = str(_s)
        o = str(_o)
        if not s in subjects :
            subjects[s] = np.array([0.0] * _len_voc)
        if not validators.url(o):
            subjects[s] += sentence_to_vector(o)
    return subjects

def random_selections(data=[], k=0):
    _randed = random.choices(data, k=k)
    return _randed

# End of embedding functions
#

def parallel_running(sub1, sub2, subs1, subs2):
    if cosine_sim(v1=subs1[sub1], v2=subs2[sub2]):
        output_alignements[sub1] = sub2
    return 1

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

    objects1 = get_rdf_objects(graph1)
    vocabulary = extract_words_from_objects(objects1)
    
    objects2 = get_rdf_objects(graph2)
    find_similar_words(vocabulary, objects2)
    print('Vocabulary builded and loaded ..100%')
    # print(synonyms)
    # exit()
    subjects1 = graph_to_vect(graph1)
    print('Source Entities vectors builded and loaded ..100%')
    subjects2 = graph_to_vect(graph2)
    print('Target Entities vectors builded and loaded ..100%')
    # exit()
    # for s, _, t in graph3:
    #     if cosine_sim(v1=subjects1[str(s)], v2=subjects2[str(t)]):
    #         output_alignements[str(s)] = str(t)
    
    n = 100000
    # n = -1
    _subjects1 = list(subjects1.keys())
    _subjects2 = list(subjects2.keys())
    pairs = list(itertools.product(_subjects1, _subjects2))
    print(f'{len(pairs)} pairs ')
    pairs = random_selections(pairs, k=n) if n > 0 else pairs
    with multiprocessing.Pool(processes=10) as pool:
        _ = pool.starmap(parallel_running, [ (sub1, sub2, subjects1, subjects2) for sub1, sub2 in tqdm(pairs)] )

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

    # file1 = "./inputs/doremus/source.ttl"
    # file2 = "./inputs/doremus/target.ttl"

    # file1 = "./inputs/agrold/source.nt"
    # file2 = "./inputs/agrold/target.nt"

    # file1 = "./inputs/anatomy/source.owl"
    # file2 = "./inputs/anatomy/target.owl"

    file1 = "./inputs/SPIMBENCH_small-2016/source.nt"
    file2 = "./inputs/SPIMBENCH_small-2016/target.nt"

    # file1 = "./inputs/spaten_hobbit/source.nt"
    # file2 = "./inputs/spaten_hobbit/target.nt"
    process_rdf_files(file1, file2)
