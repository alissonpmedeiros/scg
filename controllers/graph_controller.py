import typing 
if typing.TYPE_CHECKING:    
    """ model modules"""
    from models.mec import Mec as Mec
    from models.base_station import BaseStation as BaseStation

from models.graph import Graph as Graph

""" controller modules """
from controllers import mec_controller as mec
from controllers import bs_controller as bs
 

"""other modules"""
from typing import List
#TODO: we have to add the computing latencies of each mec node to the graph
class GraphController:
    @staticmethod
    def get_graph(base_station_set: List['BaseStation'], mec_set: List['Mec']) -> Graph:
        """ constructs the graph based on the base station and mec servers data """
        nodes = []
        for base_station in base_station_set:
            nodes.append(base_station.name)
        
        from pprint import pprint as pprint
        #pprint(nodes)
        #a = print('\n\n')
        
        """ init the graph with base stations ids """
        init_graph = {}
        for node in nodes:
            init_graph[node] = {}

        """ adds the destinations on each source node and the latency (weight) between them """
        for src_bs in base_station_set:
            src_bs_name = src_bs.name
            src_bs_mec = mec.MecController.get_mec(mec_set, src_bs)
            init_graph[src_bs_name]['computing_latency'] = src_bs_mec.computing_latency 
            for destination, value in src_bs.links.items():
                destination_bs = bs.BaseStationController.get_base_station(
                    base_station_set, destination
                )
                destination_bs_name = destination_bs.name
                destination_bs_mec = mec.MecController.get_mec(mec_set, destination_bs)
                init_graph[src_bs_name][destination_bs_name] = {'network_latency': value['latency'], 'computing_latency': destination_bs_mec.computing_latency} 
                
        """ constructs the graph """
        graph = Graph(nodes, init_graph)
        #pprint(graph.graph)
        # = input('')
        return graph


