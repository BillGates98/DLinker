import os
import logging as log
from handle_predicates import HandlePredicates
from compute_similars_pairs_predicates import ComputeSimilarPredicate
from compute_files import ComputeFile
import time

class Main: 

    
    def __init__(self, input_path='', output_path=''):
        self.input_path = input_path
        self.output_path = output_path
        self.input_files = []
        self.start_time = time.time()
        log.info('###   Predicates similarities started    ###')
    
    def run(self):
        inputs, _, graphs = ComputeFile(input_path=self.input_path, output_path=self.output_path).build_list_files()
        log.warning("Start similarity predicates protocol between datasets ...")
        dataset_predicates = []
        try :
            dataset_predicates = HandlePredicates(input_files=inputs, graphs=graphs).run()
            couples = ComputeSimilarPredicate(predicates=dataset_predicates, graphs=graphs).run()
        except RuntimeError:
            log.error("Increasing on each dataset -> Failed")
        print("--- %s seconds ---" % (time.time() - self.start_time))

Main(input_path='./inputs/', output_path='./outputs/').run()