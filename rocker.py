import rocker
import argparse

class RDFKeyDiscovery:
    def __init__(self, rdf_file='', output_path=''):
        self.rdf_file = rdf_file
        self.graph = None
        self.output_path = output_path
        self.candidate_keys = []

    def load_rdf_data(self):
        with open(self.rdf_file, 'r', encoding='utf-8') as file:
            rdf_data = file.read()
        self.graph = rocker.RDFGraph(data=rdf_data)

    def discover_candidate_keys(self):
        if not self.graph:
            self.load_rdf_data()

        key_discovery = rocker.KeyDiscovery(self.graph)
        key_discovery.run()

        self.candidate_keys = key_discovery.candidate_keys

    def get_candidate_keys(self):
        return self.candidate_keys

if __name__ == '__main__' :
    def arg_manager():
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", type=str, default="./inputs/doremus/source.ttl")
        parser.add_argument("--output_path", type=str, default="./outputs/doremus/")
        return parser.parse_args()
    args = arg_manager()
    key_discovery = RDFKeyDiscovery(rdf_file=args.file, output_path=args.output_path)
    key_discovery.discover_candidate_keys()

    candidate_keys = key_discovery.get_candidate_keys()

    print("Keys candidates : ")
    for key in candidate_keys:
        print(key)
