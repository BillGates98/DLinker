import xlwt
import time
from datetime import datetime, timedelta, date
import numpy as np
import matplotlib.pyplot as plt
import os as os
import csv
import math
import pandas as pd

class dump:

    def __init__(self):
        self.workbook = xlwt.Workbook()
        # print('Writing to file will start')
    
    def write_to_csv(self, file_name = '', entries=[] ):
        with open('./profiling_output/'+ file_name +'.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for data in entries : 
                writer.writerow(data)
                
    def write_to_txt(self, file_path='', values=[]):
        with open(file_path, 'a') as f:
            f.writelines('\n'.join(values))
            f.writelines('\n')

    def write_to_xls(self, file_name = '', colsnames=[], entries=[]):
        count_sheet = 0
        subcolsnames = []
        subentries = []
        count_parts = math.ceil(len(entries) / 254)

        start = 0
        end = 254
        for p in range(count_parts) : 
            subcolsnames = colsnames[start:end]
            subentries = entries[start:end]
            start = end + 1
            end = end + 254
            self.sub_write_to_xls(sheet='Feuille ' + str(p), colsnames=subcolsnames, entries=subentries)

        self.workbook.save('./profiling_output/'+ file_name+'.xls')
        print("Save successful")
    
    def sub_write_to_xls(self, sheet='', colsnames=[], entries=[]):
        self.sheet = self.workbook.add_sheet(sheet)

        size_col_name = len(colsnames)
        if size_col_name>0:
            for d in range(size_col_name) :
                self.sheet.write(0, d, colsnames[d])

        for d in range(len(entries)):
            for i in range(len(entries[d])):
                if entries[d][i] == 'nan' :
                    entries[d][i] = 0.0
                self.sheet.write(i+1, d if size_col_name > 0 else d, entries[d][i])

    def write_to_csv_panda(self,file_name='', data={}):
        df = pd.DataFrame(data)
        df.to_csv(file_name + '.csv', index=False, header=True)
    
    def read_csv(self, file_name=''):
        df = pd.read_csv(file_name)
        return df
    
    def write_tuples_to_csv(self,file_name='', data=[], columns=[]):
        if len(data) > 0:
            _data = {}
            for i in range(len(columns)) :
                _data[columns[i]] = []
                for d in data:
                    _data[columns[i]].append(d[i])
            df = pd.DataFrame(_data)
            df.to_csv(file_name + '.csv', mode='a', index=False, header=False)

    def dump_r(self, file_name = '', names=[], entries=[]):
        self.sheet = self.workbook.add_sheet('data')
        for i in range(len(names)):
            self.sheet.write(0, i, names[i])
        time.sleep(1)
        for d in range(0, len(entries)):
            for i in range(len(entries[d])):
                if entries[d][i] == 'nan' :
                    entries[d][i] = -1
                self.sheet.write(i+1, d, entries[d][i])
        self.workbook.save('./profiling_output/'+ file_name+'.xls')
        print("Save successful")
    