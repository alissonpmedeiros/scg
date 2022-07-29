""" other modules """
import statistics, yaml
#import numpy as np
import pandas as pd
#import seaborn as sns
from empiricaldist import Cdf  # pip install empiricaldist
import matplotlib.pyplot as plt
from pprint import pprint as pprint

""" controller modules """
from controllers import config_controller as config

CONFIG = config.ConfigController.get_config()
RESULTS_DIR = CONFIG['SYSTEM']['RESULTS_DIR']

class BoxPlot:

    @staticmethod
    def get_box_plot_data(labels, bp):
        rows_list = []

        for i in range(len(labels)):
            dict1 = {}
            dict1['label'] = labels[i]
            dict1['lower_whisker'] = bp['whiskers'][i*2].get_ydata()[1]
            dict1['lower_quartile'] = bp['boxes'][i].get_ydata()[1]
            dict1['median'] = bp['medians'][i].get_ydata()[1]
            dict1['upper_quartile'] = bp['boxes'][i].get_ydata()[2]
            dict1['upper_whisker'] = bp['whiskers'][(i*2)+1].get_ydata()[1]
            #dict1['caps'] = bp['caps'][(i*2)+1].get_ydata()[1]
            #dict1['fliers'] = bp['fliers'][i].get_ydata()
            rows_list.append(dict1)
        #pprint(rows_list)
        for row in rows_list:
            print('label:', row['label'])
            print('lower whisker=', row['lower_whisker'],',')
            print('lower quartile=', row['lower_quartile'],',')
            print('median=', row['median'],',')
            print('upper quartile=', row['upper_quartile'],',')
            print('upper whisker=', row['upper_whisker'],',')
            print('\n')
            
        return rows_list


class Results:
    @staticmethod
    def read_files(files):
        number_of_users = 1000
        labels = ['gpu_usage', 'net_latency', 'comput_latency', 'ete_latency', 'successfull', 'unsucessful', 'energy', 'hmd_energy', 'services_on_hmds']
        
        for file in files:
            gpu, net, computing, ete, sucessful, unsuccessful, energy, hmd_energy, services_on_hmds = DataFrame.get_df_data(file, number_of_users)
            
            bp = plt.boxplot([gpu, net, computing, ete, sucessful, unsuccessful, energy, hmd_energy, services_on_hmds], labels=labels)
            #bp = plt.boxplot([gpu, net, computing, ete, sucessful, unsuccessful], labels=files)
            print('FILE: {}'.format(file))
            BoxPlot.get_box_plot_data(labels, bp)
            print('\n###########################\n')

class DataFrame:
    
    @staticmethod
    def get_df_data(file_name: str, number_of_users: int):
        #FILE = '/home/ubuntu/results/results-{}/{}.csv'.format(number_of_users, file_name)
        #FILE = '/home/ubuntu/scg/results/{}.csv'.format(file_name)
        file = '{}{}.csv'.format(RESULTS_DIR, file_name)
        data_frame = pd.read_csv(file)
        data1 = data_frame.gpu_usage
        data2 = data_frame.net_latency
        data3 = data_frame.comput_latency
        data4 = data_frame.ete_latency
        data5 = data_frame.successful
        data6 = data_frame.unsuccessful
        data7 = data_frame.energy
        data8 = data_frame.hmd_energy
        data9 = data_frame.services_on_hmds
        return data1, data2, data3, data4, data5, data6, data7, data8, data9
    
    
class Histogram:
    
    @staticmethod
    def generate_histograms(experiments, files):
        for experiment in experiments:
            number_of_users = experiment
            print('\n###########################\n')
            print('EXPERIMENT: {}'.format(experiment))
            for file in files:
                gpu, net, computing, ete, sucessful, unsuccessful, energy, hmd_energy, services_on_hmds = DataFrame.get_df_data(file, number_of_users)
                
                #bp = plt.boxplot([data1, data2, data3, data4, data5, data6], labels=labels)
                #bp = plt.boxplot([gpu, net, computing, ete, sucessful, unsuccessful], labels=files)
                #BoxPlot.get_box_plot_data(labels, bp)
                
                #print('\n\n')
                #print(f'STD of algorithm {file}')
                #print(f'STD GPU: {np.std(gpu, ddof=1)}')
                #print(f'STD NET: {np.std(net, ddof=1)}')
                #print(f'STD COMPUTING: {np.std(computing, ddof=1)}')
                #print(f'STD ETE: {np.std(ete, ddof=1)}')
                #print(f'STD SUCESSFUL: {np.std(sucessful, ddof=1)}')
                #print(f'STD UNSUCESSFUL: {np.std(unsuccessful, ddof=1)}')
                #print(f'STD ENERGY: {np.std(energy, ddof=1)}')
                #print(f'STD HMD_ENERGY: {np.std(hmd_energy, ddof=1)}')
                #print(f'STD SERVICES_ON_HMD: {np.std(services_on_hmds, ddof=1)}')
                
                print('\n')
                print(f'Means of algorithm {file}')
                #print(f'GPU: {statistics.mean(gpu)}')
                print(f'NET: {statistics.mean(net)}')
                #print(f'COMPUTING: {statistics.mean(computing)}')
                print(f'ETE: {statistics.mean(ete)}')
                #print(f'SUCESSFUL: {statistics.mean(sucessful)}')
                #print(f'UNSUCESSFUL: {statistics.mean(unsuccessful)}')
                print(f'ENERGY: {statistics.mean(energy)}')
                print(f'HMD_ENERGY: {statistics.mean(hmd_energy)}')
                print(f'SERVICES_ON_HMD: {statistics.mean(services_on_hmds)}')
                
                #n_bins = 200
                #fig, axs = plt.subplots(3, 2, tight_layout=True)
                #fig.suptitle('Algorithm {} | Vr users {}'.format(file, number_of_users))
                
                """
                #GPU usage
                axs[0, 0].hist(gpu, bins=n_bins)
                axs[0, 0].set_title('gpu usage')
                axs[0, 0].set_xlabel('number of gpus')
                axs[0, 0].set_ylabel('frequency')
                
                #net latency
                axs[0, 1].hist(net, bins=n_bins)
                axs[0, 1].set_title('network latency')
                axs[0, 1].set_xlabel('latency (ms)')
                axs[0, 1].set_ylabel('frequency')
                
                #computing latency
                axs[1, 0].hist(computing, bins=n_bins)
                axs[1, 0].set_title('computing latency')
                axs[1, 0].set_xlabel('latency (ms)')
                axs[1, 0].set_ylabel('frequency')
                
                #e2e latency
                axs[1, 1].hist(ete, bins=n_bins)
                axs[1, 1].set_title('e2e latency')
                axs[1, 1].set_xlabel('latency (ms)')
                axs[1, 1].set_ylabel('frequency')
                
                #successful migrations
                axs[2, 0].hist(sucessful, bins=n_bins)
                axs[2, 0].set_title('sucessful migrations')
                axs[2, 0].set_xlabel('number of migration')
                axs[2, 0].set_ylabel('frequency')
                
                #unsuccessful migrations
                axs[2, 1].hist(unsuccessful, bins=n_bins)
                axs[2, 1].set_title('unsuccessful migrations')
                axs[2, 1].set_xlabel('number of migrations')
                axs[2, 1].set_ylabel('frequency')
                """
                
                plt.show(block=False)
                
        plt.show()
            


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
    def generate_cdf(experiments, files):
        for experiment in experiments:
            number_of_users = experiment
            
            for file in files:
                gpu, net, computing, ete, sucessful, unsuccessful, energy, hmd_energy, services_on_hmds = DataFrame.get_df_data(file, number_of_users)
    
                
                fig, axs = plt.subplots(3, 2, tight_layout=True, figsize=(16, 8))
                fig.suptitle('CDF of Algorithm {} | Vr users {}'.format(file, number_of_users))
                #GPU usage
                cdf_data = Cdf.from_seq(gpu)
                axs[0, 0].plot(cdf_data)
                axs[0, 0].set_title('gpu usage')
                axs[0, 0].set_xlabel('number of gpus')
                axs[0, 0].set_ylabel('probability')
                
                #net latency
                cdf_data = Cdf.from_seq(net)
                axs[0, 1].plot(cdf_data)
                axs[0, 1].set_title('network latency')
                axs[0, 1].set_xlabel('latency (ms)')
                axs[0, 1].set_ylabel('frequency')
                
                #computing latency
                cdf_data = Cdf.from_seq(computing)
                axs[1, 0].plot(cdf_data)
                axs[1, 0].set_title('computing latency')
                axs[1, 0].set_xlabel('latency (ms)')
                axs[1, 0].set_ylabel('frequency')
                
                #e2e latency
                cdf_data = Cdf.from_seq(ete)
                axs[1, 1].plot(cdf_data)
                axs[1, 1].set_title('e2e latency')
                axs[1, 1].set_xlabel('latency (ms)')
                axs[1, 1].set_ylabel('frequency')
                
                """
                #successful migrations
                cdf_data = Cdf.from_seq(sucessful)
                axs[2, 0].plot(cdf_data)
                axs[2, 0].set_title('sucessful migrations')
                axs[2, 0].set_xlabel('number of migration')
                axs[2, 0].set_ylabel('frequency')
                
                #if file != 'no':
                #    print(f'\n\nCDF of algorithm {file} | successful')
                #    CDF.print_PDF(cdf_data)
                #unsuccessful migrations
                cdf_data = Cdf.from_seq(unsuccessful)
                axs[2, 1].plot(cdf_data)
                axs[2, 1].set_title('unsuccessful migrations')
                axs[2, 1].set_xlabel('number of migrations')
                axs[2, 1].set_ylabel('frequency')
                """
                #HMD energy consumption
                cdf_data = Cdf.from_seq(hmd_energy)
                axs[2, 1].plot(cdf_data)
                axs[2, 1].set_title('HMD energy consumption')
                axs[2, 1].set_xlabel('Energy (J)')
                axs[2, 1].set_ylabel('frequency')
                
                #HMD energy consumption
                cdf_data = Cdf.from_seq(energy)
                axs[2, 1].plot(cdf_data)
                axs[2, 1].set_title('Energy consumption')
                axs[2, 1].set_xlabel('Energy (J)')
                axs[2, 1].set_ylabel('frequency')
                
                print(f'\n\nCDF of algorithm {file} | HMD energy')
                CDF.print_PDF(cdf_data)
                plt.show(block=False)
                
        
        plt.show()
                
                


if __name__ == "__main__":
    #files = ['scg', 'network-resource', 'network', 'always', 'no']
    files = ['scg']
    experiments = [1000]
    Histogram.generate_histograms(experiments, files)
    
    #files = ['scg']
    #experiments = [1000]
    #CDF.generate_cdf(experiments, files)
    #Results.read_files(files)