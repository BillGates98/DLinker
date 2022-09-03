import os
import logging as log
from handle_predicates import HandlePredicates
from compute_similars_pairs_predicates import ComputeSimilarPredicate
from compute_files import ComputeFile
import time
import argparse

class Main: 

    def __init__(self, input_path='', output_path='', alpha_predicate=0):
        self.input_path = input_path
        self.output_path = output_path
        self.input_files = []
        self.start_time = time.time()
        self.alpha_predicate = alpha_predicate
        log.info('###   Predicates similarities started    ###')
    
    def run(self):
        inputs, _, graphs = ComputeFile(input_path=self.input_path, output_path=self.output_path).build_list_files()
        log.warning("Start similarity predicates protocol between datasets ...")
        dataset_predicates = []
        try :
            dataset_predicates = HandlePredicates(input_files=inputs, graphs=graphs).run()
            couples = ComputeSimilarPredicate(predicates=dataset_predicates, graphs=graphs, alpha_predicate=self.alpha_predicate).run()
        except RuntimeError:
            log.error("Increasing on each dataset -> Failed")
        print("--- %s seconds ---" % (time.time() - self.start_time))


if __name__ == '__main__' :
    def arg_manager():
        parser = argparse.ArgumentParser()
        parser.add_argument("--alpha_predicate", type=float, default=1)
        parser.add_argument("--alpha", type=float, default=0.88)
        parser.add_argument("--phi", type=int, default=2)
        parser.add_argument("--measure_level", type=int, default=1)
        return parser.parse_args()
    args = arg_manager()
    Main(input_path='./inputs/', output_path='./outputs/', alpha_predicate=args.alpha_predicate).run()