from fileinput import filename
from tkinter.tix import COLUMN
import matplotlib.pyplot as plt
import random
import pandas as pd
from pprint import pprint as pprint 
import numpy as np

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
            print('{}: {}'.format(row['label'], row['median']))
        return rows_list


class DataFrame:
    
    @staticmethod
    def get_df_data(file_name: str):
        #FILE = '/home/ubuntu/scg/results/{}.csv'.format(file_name)
        FILE = '/home/ubuntu/results/results-1000/{}.csv'.format(file_name)
        data_frame = pd.read_csv(FILE)
        #data = data_frame.gpu_usage
        #data1 = data_frame.ete_latency
        data2 = data_frame.successful
        data1 = data_frame.unsuccessful
        return data1, data2
    
if __name__ == "__main__":
    files = ['react', 'scg', 'network-resource', 'network', 'always', 'no']
    
    computing, network = DataFrame.get_df_data(files[2])
    '''
    data1 = DataFrame.get_df_data(files[0])
    data2 = DataFrame.get_df_data(files[1])
    data3 = DataFrame.get_df_data(files[2])
    data4 = DataFrame.get_df_data(files[3])
    data5 = DataFrame.get_df_data(files[4])
    data6 = DataFrame.get_df_data(files[5])
    '''
    
    labels = ['computing', 'network']
    #labels = ['react', 'scg', 'resource', 'network', 'always', 'no']
    #bp = plt.boxplot([data1, data2, data3, data4, data5, data6], labels=labels)
    bp = plt.boxplot([computing, network], labels=labels)
    #pprint(bp)
    #a = input('')
    #BoxPlot.get_box_plot_data(labels, bp)
    '''
    print('\n\n')
    print(f'STD react: {np.std(data1, ddof=1)}')
    print(f'STD scg: {np.std(data2, ddof=1)}')
    print(f'STD resource: {np.std(data3, ddof=1)}')
    print(f'STD network: {np.std(data4, ddof=1)}')
    print(f'STD always: {np.std(data5, ddof=1)}')
    print(f'STD no: {np.std(data6, ddof=1)}')
    '''
    n_bins = 200
    fig, axs = plt.subplots(1, 2, tight_layout=True)
    axs[0].hist(computing, bins=n_bins)
    axs[1].hist(network, bins=n_bins)

    
    plt.show()
    '''
    '''
    
    
    
