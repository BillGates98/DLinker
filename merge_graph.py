import os
import log
from datetime import datetime
from compute_files import ComputeFile
from rdflib import Graph, Literal
from rdflib.namespace import RDF

class MergeGraph: 

    def __init__(self, input_path='', output_path=''):
        self.input_path = input_path
        self.output_path = output_path
        now = datetime.now()
        date_string = now.strftime("%m/%d/%Y at %H:%M:%S")
        log.info('###   Merge Graph process started the ' + date_string + '  ###')


    def load_graph(self, graph=Graph(), input_file=''):
        """
            expands the data and puts the new version in the associated output file
        """
        try:
            graph.parse(input_file)
        except Exception as _ :
            log.critical('#Not converted to graph >> ' + input_file + ' ....%')
        return graph


    def run(self):
        """
            Merge graphs process
        """
        inputs, outputs = ComputeFile(input_path=self.input_path, output_path=self.output_path).build_list_files_without_graphs()
        log.info('Input Files')
        log.info(inputs)
        log.info('Output Files')
        log.info(outputs)
        log.warning("Start merge graph from each dataset ...")
        graphs = Graph()
        try :
            for i in range(len(inputs)):
                try:
                    graphs = self.load_graph(graph=graphs, input_file=inputs[i])
                except UnicodeDecodeError:
                    log.error("File content errors : " + inputs[i])
                    continue
            try:
                graphs.serialize(destination=self.output_path + 'merged_graphs.ttl', format='turtle')
                # log.info(g.serialize(format="turtle").decode("UTF-8"))    
            except Exception :
                log.info('Exception during the merge process ')
            now = datetime.now()
            date_string = now.strftime("%m/%d/%Y at %H:%M:%S")
            log.info('End of the merge graph process the ' + date_string)
        except RuntimeError:
            log.error("Merge Graph from each dataset -> Failed")

MergeGraph(input_path='./inputs/', output_path='./outputs/').run()
