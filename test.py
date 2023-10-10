import json
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

from tqdm import tqdm

# output_file = './outputs/doremus/tmp_same_as.ttl'
# truth_file = './validations/doremus/valid_same_as.ttl'

output_file = './outputs/agrold/tmp_same_as.ttl'
truth_file = './validations/agrold/valid_same_as.ttl'

def sigmoid(value):
    return 1 / (1 + np.exp(value))

def cosine_sim(v1=[], v2=[]):
    output = 0.0
    dot = np.dot(v1, v2)
    output = sigmoid(dot)
    if output <= 0.10  :
        # print(output)
        return True
    return False

def extract_entity_vectors_rdf(graph, index, embedding_dim=1000):
    nx_graph = rdflib_to_networkx_multidigraph(graph)

    node2vec = Node2Vec(nx_graph, dimensions=64, walk_length=30, num_walks=20, workers=4)

    model = node2vec.fit(window=10, min_count=1, batch_words=4)  

    return model # model.wv['subject']

def calculate_alignment_metrics(output_file, truth_file):
    output_graph = Graph()
    output_graph.parse(output_file, format="turtle")

    truth_graph = Graph()
    truth_graph.parse(truth_file, format="turtle")

    found_alignments = set(output_graph.subjects())
    true_alignments = set(truth_graph.subjects())

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

def random_choice(value='', data=[], n = 500):
    ds = DeepSimilarity(code='*')
    score = 0.0
    _object = ''
    _data = random.choices(data, k=n)
    values = [ ds.jaro_similarity(value1=value, value2=d)  for d in _data ]
    score = max(values)
    index = values.index(score)
    _object = _data[index]
    return score, _object

def process_rdf_files(file1, file2):
    graph1 = Graph()
    graph1.parse(file1)
    vectors1 = extract_entity_vectors_rdf(graph=graph1, index=1)

    graph2 = Graph()
    graph2.parse(file2)  
    vectors2 = extract_entity_vectors_rdf(graph=graph2, index=2)

    os1 = {}
    _alignements = {}

    _g1_length = len(graph1)
    _g2_length = len(graph2)
    _graph1 = graph1 if  _g1_length >= _g2_length else graph2
    _graph2 = graph2 if  _g1_length >= _g2_length else graph1
    rand_count = int(( _g1_length if  _g1_length >= _g2_length else _g2_length ) * 0.08)
    for s1, p1, o1 in tqdm(_graph1):
        _o1 = str(o1)
        _s1 = str(s1)
        if not validators.url(_o1) :
            if not _o1 in os1 : 
                os1[_o1] = set()
            os1[_o1].add(_s1)

    objects1 = list(os1.keys())
    for s2, p2, o2 in tqdm(_graph2) :
        _o2 = str(o2)
        _s2 = str(s2)
        if not validators.url(_o2) :
            score, object1 = random_choice(value=_o2, data=objects1, n=rand_count)
            sub_s1 = os1[object1]
            for s1 in sub_s1:
                _s1 = str(s1)
                subpair = _s1 + "@" + _s2
                if _s1 in vectors1.wv and _s2 in vectors2.wv and cosine_sim(v1=vectors1.wv[_s1], v2=vectors2.wv[_s2]) : 
                    if not subpair in _alignements :
                        _alignements[subpair] = 0
                    _alignements[subpair] += 1
    # print(json.dumps(keys_candidates, indent=4))
    print(' \n \n ')
    tmp = {}
    count = 0
    for key in _alignements:
        _tmp = _alignements[key]
        if _tmp >= 1 : 
            parts = key.split('@')
            tmp[parts[0]] = parts[1]
            count+=1
    # print(json.dumps(tmp, indent=4))
    print(f'They are {len(list(tmp.keys()))} in all')
    create_and_save_rdf_from_dict(tmp, output_file)
    metrics = calculate_alignment_metrics(output_file, truth_file)
    print("Precision : ", metrics["precision"])
    print("Recall : ", metrics["recall"])
    print("F-measure : ", metrics["f_measure"])

if __name__ == "__main__":

    # file1 = "./inputs/doremus/source.ttl"
    # file2 = "./inputs/doremus/target.ttl"

    file1 = "./inputs/agrold/source.nt"
    file2 = "./inputs/agrold/target.nt"
    process_rdf_files(file1, file2)
