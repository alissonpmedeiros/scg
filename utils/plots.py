""" other modules """
import statistics, yaml
from typing import Any
#import numpy as np
import pandas as pd
#import seaborn as sns
from empiricaldist import Cdf  # pip install empiricaldist
import matplotlib.pyplot as plt
from pprint import pprint as pprint

""" controller modules """
#from controllers import config_controller as config_controller
from .. controllers import config_controller
from . csv_encoder import CSV
""" other modules """
import os
 

CONFIG = config_controller.ConfigController.get_config()
RESULTS_DIR = CONFIG['SYSTEM']['RESULTS_DIR']
    
class DataFrame:
    
    @staticmethod
    def get_df_data(file_dir: str, file_name: str):
        file = '{}{}.csv'.format(file_dir, file_name)
        
        data_frame = pd.read_csv(file)
        return data_frame
    
    @staticmethod
    def calculate_average(data_frame: Any, kpi: str):
        df_mean = data_frame[[kpi]].mean()
        return round(float(df_mean), 2)
    
    
    @staticmethod
    def calculate_std(data_frame: Any, kpi: str):
        df_std = data_frame[[kpi]].std()
        return round(float(df_std), 2)
    
    

class Results:
    
    @staticmethod
    def read_files(file_dir: str, cities: dict, algorithms: list):
        
        results = {
            'bern':   {},
            'geneva': {},
            'zurich': {}       
        }
        
        for city, radius in cities.items():
            #print(f'\n##################################################')
            #print(f'City of {city}')
            for r in radius: 
                radius_name = 'r_0{}'.format(r)
                #print(f'__________________________________')
                #print(f'\n*** radius: {radius_name} ***')
                radius_dir = '{}/{}/{}/'.format(file_dir, city, radius_name)
                results[city][radius_name] = {}
                for algorithm in algorithms:
                    #print(f'\nalgorithm: {algorithm}')
                    result = DataFrame.get_df_data(radius_dir, algorithm)
                    results[city][radius_name][algorithm] = result
            
            #print(f'\n##################################################\n')
        #print(results)
        #a = input('')
        return results
    
    @staticmethod
    def create_overleaf_topology_directories_(overleaf_dir: str, cities: dict):
        """ creates the directories for each topology into overleaf dir """
        for city, radius in cities.items():
            city_dir = os.path.join(overleaf_dir, city)
            if not os.path.exists(city_dir):
                os.mkdir(city_dir)
                '''
                for r in radius: 
                    radius_name = 'r_0{}'.format(r)
                    radius_dir = os.path.join(city_dir, radius_name)
                    if not os.path.exists(radius_dir):
                        os.mkdir(radius_dir)
                '''
                
       
    @staticmethod
    def get_bar_plot_file_header(energy=False, latency=False):
        global algorithms
        file_header = []
        file_header.append('x')
        for algorithm in algorithms:
            file_header.append(algorithm)
            if energy:
                file_header.append(str(algorithm+'-hmd'))
            elif latency:
                file_header.append(str(algorithm+'-net'))
            
            file_header.append(str(algorithm+'-std'))
        
        return file_header

    @staticmethod
    def get_line_plot_file_header():
        global algorithms
        file_header = []
        file_header.append('x')
        
        for algorithm in algorithms:
            file_header.append(algorithm)
        
        return file_header
    
    @staticmethod
    def get_box_plot_file_header():
        global algorithms
        file_header = []
        
        for algorithm in algorithms:
            file_header.append(algorithm)
        
        return file_header
                
class BarPlot:                
    
    """
    all methods receive a DataFrame and produces a csv file that will be used by overleaf
    """
    
    @staticmethod
    def create_bar_plot(overleaf_dir: str, results: dict, kpi: str):
        """ 
        Can be used by all other KPIs
        1. first row is x, which represents the radius for a specific topology
        2. other rows are specified according to each algorithm 
        3. each algorithm has the following rows: alg-name and alg-std, where for latency and energy plots there are alg-net and alg-hmd fields, respectively
        """
        for city, radius in results.items():
            #print(f'city: {city}')
            city_dir = '{}{}/'.format(overleaf_dir, city)
            file_name = '{}_{}_bar.csv'.format(city, kpi)
            file_headers = None
            if kpi == 'ete_latency':
                file_headers= Results.get_bar_plot_file_header(latency=True)
            elif kpi == 'energy':
                file_headers = Results.get_bar_plot_file_header(energy=True)
            else:
                file_headers = Results.get_bar_plot_file_header()
                
             
            CSV.create_file(city_dir, file_name, file_headers)
            
            x_value = 100
            for radius_id, algorithms in radius.items():
                #print(f'\n\nradius: {radius_id}\n')
                algorithms_performance = []
                algorithms_performance.append(x_value)
                
                for algorithm, alg_data_frame in algorithms.items(): 
                    alg_avg = DataFrame.calculate_average(alg_data_frame, kpi)
                    
                    algorithms_performance.append(alg_avg)
                    
                    if kpi == 'ete_latency':
                        net_avg = DataFrame.calculate_average(alg_data_frame, 'net_latency')
                        algorithms_performance.append(net_avg)
                    elif kpi == 'energy':
                        hmd_energy_avg = DataFrame.calculate_average(alg_data_frame, 'hmd_energy')
                        algorithms_performance.append(hmd_energy_avg)
                    
                    alg_std = DataFrame.calculate_std(alg_data_frame, kpi)
                    
                    if kpi == 'successful' or kpi == 'unsuccessful' or kpi == 'exec':
                        alg_std = alg_std / 10
                    
                    algorithms_performance.append(alg_std)
                
                CSV.save_data(city_dir, file_name,algorithms_performance )
                x_value += 450
                
    @staticmethod
    def create_bar_plots(overleaf_dir: str, results: dict):
        global bar_plot_kpis
        for kpi in bar_plot_kpis:
            BarPlot.create_bar_plot(overleaf_dir, results, kpi)
            
    
class LinePlot:
    
    """
    all methods receive a DataFrame and produces a csv file that will be used by overleaf
    """
    @staticmethod
    def create_x_row():
        x_row = []
        for i in range(1, 301):
            x_row.append(round((i / 30), 2))
        
        #print(x_row)
        return x_row
    
    @staticmethod 
    def create_line_plot(overleaf_dir: str, results: dict, kpi: str):
        """
        1. first row is x and this represents the time in hours (10h). 
        2. X row is generated based on a loop that ranges from 1 to 300, each value of each line of X is calculated based on: iteration/300. 
        3. reads each file, delete the first result, and get first 100 values of it in each radius. in the end, there will be 300 values for the 3 radius. Store them on a list.
        """
        for city, radius in results.items():
            city_dir = '{}{}/'.format(overleaf_dir, city)
            file_name = '{}_{}_line.csv'.format(city, kpi)
            file_headers = Results.get_line_plot_file_header()
                
             
            CSV.create_file(city_dir, file_name, file_headers)
            
            x_row = LinePlot.create_x_row()
            position = 0
            
            for radius_id, algorithms in radius.items():
                #print(f'radius: {radius_id}')
                for i in range(100):
                    line_list = []
                    line_list.append(x_row[position])
                    for algorithm, alg_data_frame in algorithms.items():
                        kpi_result = alg_data_frame[kpi].iloc[i]
                        line_list.append(kpi_result)
                
                    #print(line_list)
                    CSV.save_data(city_dir, file_name, line_list)
                    position += 1   
                
            
class BoxPlot:
    @staticmethod 
    def create_boxplot(overleaf_dir: str, results: dict, kpi: str):
        """for each radius, it creates files without X column for overleaf boxplot"""
        for city, radius in results.items():
            city_dir = '{}{}/'.format(overleaf_dir, city)
            
            for radius_id, algorithms in radius.items():
                
                file_name = '{}_{}_{}_box.csv'.format(city, kpi, radius_id)
                file_headers = Results.get_box_plot_file_header()
                
                CSV.create_file(city_dir, file_name, file_headers)
            
                min_lines = float('inf')
                for algorithm, alg_data_frame in algorithms.items():
                    number_lines = len(alg_data_frame)
                    if number_lines < min_lines:
                        min_lines = number_lines
                        
                for i in range(min_lines):
                    line_list = []
                    for algorithm, alg_data_frame in algorithms.items():
                        kpi_result = alg_data_frame[kpi].iloc[i]
                        line_list.append(kpi_result)
                
                    CSV.save_data(city_dir, file_name, line_list)
  
                
                
            
if __name__ == "__main__":

    algorithms = ['dscp', 'scg', 'lra', 'am', 'la']
    overleaf_dir = '/home/ubuntu/overleaf/'
    
    cities = {
        'bern':   [18, 23, 29],
        'geneva': [15, 17, 19],
        'zurich': [16, 19, 22]       
    }
    
    bar_plot_kpis = ['ete_latency', 'energy', 'successful', 'unsuccessful', 'exec']
    
    Results.create_overleaf_topology_directories_(overleaf_dir, cities)
    results = Results.read_files(RESULTS_DIR, cities, algorithms)
    #BarPlot.create_bar_plots(overleaf_dir, results)
    #LinePlot.create_line_plot(overleaf_dir, results, 'ete_latency')
    BoxPlot.create_boxplot(overleaf_dir, results, '1080p')
    BoxPlot.create_boxplot(overleaf_dir, results, '1440p')
    BoxPlot.create_boxplot(overleaf_dir, results, '4k')
    BoxPlot.create_boxplot(overleaf_dir, results, '8k')
    
    

'''
        
class CDF:
    
    @staticmethod
    def print_PDF(CDF):
        #print(CDF)
        index = 0
        for c in CDF:
            print(CDF.ps[index])
            index+=1
        print('\n')
        
        index = 0
        for c in CDF:
            print(CDF.qs[index])
            index+=1
        print('\n')
        
        #a = input('')
        
    @staticmethod
    def print_PDF2(CDF):
        threshold = 0.1
        for i in range(0, 1000):
            if CDF.ps[i] > threshold:
                #print(f'{round(CDF.ps[i], 1)} -> {CDF.qs[i]}')
                print(f'{CDF.qs[i]}')
                
                threshold += 0.1
                if threshold >= 1:
                    break
    
    @staticmethod
    def generate_cdf(overleaf_dir: str, results: dict, kpi: str):
        
        kpi_data = results[[kpi]]
        print(kpi_data)
        a = input('')
        cdf_data = Cdf.from_seq(kpi_data)
        CDF.print_PDF(cdf_data)
'''