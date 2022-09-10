import os
import log
from datetime import datetime
from rdflib import Graph

class ComputeFile: 

    def __init__(self, input_path='', output_path=''):
        self.input_path = input_path
        self.output_path = output_path
        self.input_files = []
        self.output_files = []
        self.extensions = ['.ttl', '.nt']
    
    def build_graph(self, input_file=''):
        graph = Graph()
        graph.parse(input_file, format='trig')
        return graph
    
    def accept_extension(self, file='') :
        for ext in self.extensions :
            if file.endswith(ext) :
                return True
        return False
    
    def build_list_files(self):
        """
            building the list of input and output files
        """
        graphs = []
        for current_path, folders, files in os.walk(self.input_path):
            for file in files:
                if self.accept_extension(file=file):
                    tmp_current_path = os.path.join(current_path, file)
                    self.input_files.append(tmp_current_path)
                    graphs.append(self.build_graph(input_file=tmp_current_path))
                    path = current_path.replace(self.input_path, self.output_path)
                    tmp_path = os.path.join(path, file)
                    self.output_files.append(tmp_path)
        print('Input Files')
        print(self.input_files)
        print('Output Files')
        print(self.output_files)
        return self.input_files, self.output_files, graphs
    
    def build_list_files_without_graphs(self):
        """
            building the list of input and output files
        """
        for current_path, folders, files in os.walk(self.input_path):
            for file in files:
                if self.accept_extension(file=file):
                    tmp_current_path = os.path.join(current_path, file)
                    self.input_files.append(tmp_current_path)
                    path = current_path.replace(self.input_path, self.output_path)
                    tmp_path = os.path.join(path, file)
                    self.output_files.append(tmp_path)
        print('Input Files')
        print(self.input_files)
        print('Output Files')
        print(self.output_files)
        return self.input_files, self.output_files