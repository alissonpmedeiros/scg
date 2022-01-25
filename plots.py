import matplotlib.pyplot as plt
import random
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
        return rows_list

    @staticmethod
    def build_plot(labels: list, data: list):
        """
        label must follow the following paterm: labels = ['label1', 'label2',...'labeln']
        just one one label and one list of data per time
        """

        bp = plt.boxplot([data], labels=labels)
        plt.show()
        return BoxPlot.get_box_plot_data(labels, bp)

