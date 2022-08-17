import typing 
if typing.TYPE_CHECKING:    
    """ model modules"""
    from models.mec import Mec as Mec
    from models.base_station import BaseStation as BaseStation

from models.graph import Graph as Graph

""" controller modules """
from controllers import bs_controller 
from controllers import mec_controller 
 

"""other modules"""
from typing import List, Dict


class GraphController:
    @staticmethod
    def get_graph(base_station_set: Dict[str,'BaseStation'], mec_set: Dict[str,'Mec']) -> Graph:
        """ constructs the graph based on the base station and mec servers data """
        
        nodes = []
        for bs_id, base_station in base_station_set.items():
            nodes.append(base_station.name)
        
        """ init the graph with base stations ids """
        init_graph = {}
        for node in nodes:
            init_graph[node] = {}

        """ adds the destinations on each source node and the latency (weight) between them """
        for src_bs_id, src_bs in base_station_set.items():
            src_bs_name = src_bs.name
            src_bs_mec = mec_controller.MecController.get_mec(mec_set, src_bs)
            init_graph[src_bs_name]['computing_latency'] = src_bs_mec.computing_latency 
            for destination_id, value in src_bs.links.items():
                destination_bs = bs_controller.BaseStationController.get_base_station(
                    base_station_set, destination_id
                )
                destination_bs_name = destination_bs.name
                destination_bs_mec = mec_controller.MecController.get_mec(mec_set, destination_bs)
                init_graph[src_bs_name][destination_bs_name] = {'network_latency': value['latency'], 'computing_latency': destination_bs_mec.computing_latency} 
                
        """ constructs the graph """
        graph = Graph(nodes, init_graph)
        return graph


