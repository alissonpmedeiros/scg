from fileinput import filename
from tkinter.tix import COLUMN
import matplotlib.pyplot as plt
import random
import pandas as pd
from pprint import pprint as pprint 

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
            rows_list.append(dict1)
        pprint(rows_list)
        return rows_list


class DataFrame:
    
    @staticmethod
    def get_df_data(file_name: str):
        FILE = '/home/ubuntu/scg/results/{}.csv'.format(file_name)
        data_frame = pd.read_csv(FILE)
        #data = data_frame.gpu_usage
        data = data_frame.ete_latency
        #data = data_frame.net_latency
        #data = data_frame.comput_latency
        return data
    
if __name__ == "__main__":
    files = ['react', 'scg', 'network-resource', 'network', 'always', 'no']
    
    data1 = DataFrame.get_df_data(files[0])
    data2 = DataFrame.get_df_data(files[1])
    data3 = DataFrame.get_df_data(files[2])
    data4 = DataFrame.get_df_data(files[3])
    data5 = DataFrame.get_df_data(files[4])
    data6 = DataFrame.get_df_data(files[5])
    
    labels = ['react', 'scg', 'resource', 'network', 'always', 'no']
    bp = plt.boxplot([data1, data2, data3, data4, data5, data6], labels=labels)
    BoxPlot.get_box_plot_data(labels, bp)
    plt.show()
    
    
    '''
    FILE = '/home/ubuntu/scg/results/scg.csv'
    labels = ['scg']
    df = pd.read_csv(FILE)
    data = df.gpu_usage
    #for data in data:
        #print(data)
    BoxPlot.build_plot(labels, data)
    '''