from mec.mec import Mec
from typing import List
from pprint import pprint as pprint
from base_station.bs_controller import BaseStation, BaseStationController


 
class Graph():
    def __init__(self, nodes, init_graph):
        self.nodes = nodes
        self.graph = self.construct_graph(nodes, init_graph)
        
    def construct_graph(self, nodes, init_graph):
        """
        This method makes sure that the graph is symmetrical. In other words, 
        if there's a path from node A to B with a value V, there needs to be 
        a path from node B to node A with a value V.
        """
        graph = {}
        for node in nodes:
            graph[node] = {}
        
        graph.update(init_graph)
        
        for node, edges in graph.items():
            for adjacent_node, value in edges.items():
                if graph[adjacent_node].get(node, False) == False:
                    graph[adjacent_node][node] = value
                    
        return graph
    
    def get_nodes(self):
        "Returns the nodes of the graph."
        return self.nodes
    
    def get_outgoing_edges(self, node):
        "Returns the neighbors of a node."
        connections = []
        for out_node in self.nodes:
            if self.graph[node].get(out_node, False) != False:
                connections.append(out_node)
        return connections
    
    def value(self, node1, node2):
        "Returns the value of an edge between two nodes."
        return self.graph[node1][node2]


class GraphController:
    
    @staticmethod
    def get_graph(base_station_set: List[BaseStation], mec_set: List[Mec]) -> Graph:
        """ constructs the graph based on the base station and mec servers data """
        
        nodes = []
        for base_station in base_station_set:
            nodes.append(base_station.id)
        
        
        """ init the graph with base stations ids """
        init_graph = {}
        for node in nodes:
            init_graph[node] = {}

        """ adds the destinations on each source node and the latency (weight) between them """
        for base_station in base_station_set:
            scr = base_station.id
            for link in base_station.links:
                dst = link.dst.device
                dst_bs = BaseStationController.get_base_station(
                    base_station_set=base_station_set, bs_id=dst
                )
                dst_bs_mec = None
                for mec in mec_set:
                    if mec.id == dst_bs.mec_id:
                        dst_bs_mec = mec
                        break
                init_graph[scr][dst] = base_station.wireless_latency + link.latency + dst_bs_mec.computing_latency
                
        """ constructs the graph """
        graph = Graph(nodes, init_graph)
        return graph


