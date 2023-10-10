import json
from rdflib import Graph
from deep_similarity import DeepSimilarity
import numpy as np
import random
import validators
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import OWL
from rdflib import Graph
from graph2vec import Node2Vec

output_file = './outputs/doremus/tmp_same_as.ttl'

truth_file = './validations/doremus/valid_same_as.ttl'

def extract_entity_vectors(rdf_file, vector_dim=100, walk_length=30, num_walks=10):
    rdf_graph = Graph()
    rdf_graph.parse(rdf_file, format="turtle")

    rdf2vec_model = Node2Vec(
        dimensions=vector_dim,
        walk_length=walk_length,
        num_walks=num_walks,
        workers=4
    )

    rdf2vec_model.fit(rdf_graph)

    entity_vectors = {}
    for entity_uri in rdf2vec_model.wv.vocab:
        entity_vector = rdf2vec_model.wv[entity_uri]
        entity_vectors[entity_uri] = entity_vector

    return entity_vectors

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

def random_choice(value='', data=[], n = 1000):
    ds = DeepSimilarity(code='*')
    score = 0.0
    _object = ''
    _data = random.choices(data, k=n)
    for i in range(len(_data)):
        _score = ds.hamming(value1=value, value2=data[i])
        score = _score if _score >= score else score
        _object = data[i] if _score >= score else _object
    return score, _object

def process_rdf_files(file1, file2):
    graph1 = Graph()
    graph1.parse(file1)
    vectors1 = extract_entity_vectors(rdf_file=file1)

    graph2 = Graph()
    graph2.parse(file2)  
    vectors2 = extract_entity_vectors(rdf_file=file2)

    os1 = {}
    op1 = {}

    os2 = {}
    op2 = {}

    keys_candidates = {}
    
    _alignements = {}
    for s1, p1, o1 in graph1:
        if not validators.url(o1) :
            if not o1 in os1 : 
                os1[o1] = set()
            os1[o1].add(s1)

            if not o1 in op1 : 
                op1[o1] = set()
            op1[o1].add(p1)

    objects1 = list(os1.keys())
    for s2, p2, o2 in graph2 :
        if not validators.url(o2) :
            score, object1 = random_choice(value=o2, data=objects1)
            obj_p1 = op1[object1]
            sub_s1 = os1[object1]
            if score >= 0.2 :
                if not o2 in op2 : 
                    op2[o2] = set()
                os2[o2] = s2
                op2[o2].add(p2)

                for p1 in obj_p1:
                    predpair = str(p1) + "@" + str(p2)
                    if not predpair in keys_candidates :
                        keys_candidates[predpair] = 0 
                    keys_candidates[predpair] += 1
                
                for s1 in sub_s1:
                    subpair = str(s1) + "@" + str(s2)
                    if not subpair in _alignements :
                        _alignements[subpair] = 0
                    _alignements[subpair] += 1
    # print(json.dumps(keys_candidates, indent=4))
    print(' \n \n ')
    tmp = {}
    count = 0
    for key in _alignements:
        _tmp = _alignements[key]
        if _tmp >= 2 : 
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
    file1 = "./inputs/doremus/source.ttl"
    file2 = "./inputs/doremus/target.ttl"
    process_rdf_files(file1, file2)
