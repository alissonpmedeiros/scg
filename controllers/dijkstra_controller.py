import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.graph import Graph
    from models.base_station import BaseStation 

from models.dijkstra import Dijkstra
    
""" controller modules """
from controllers import mec_controller as mec

"""other modules"""
import operator
from typing import List

class DijkstraController:
    @staticmethod
    def get_ETE_latency(
        mec_set: List['Mec'], graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation' 
    ):

        #from controllers.mec_controller import MecController
        #start_node_mec = MecController.get_mec(mec_set=mec_set, mec_id=start_node.mec_id)
        
        #start_node_mec= ControllerInterface.MecController().get_mec(mec_set=mec_set, base_station=start_node)
        start_node_mec= mec.MecController.get_mec(mec_set=mec_set, base_station=start_node)
        
        
        previous_nodes, shortest_path = Dijkstra.build_shortest_path(
            graph=graph, 
            start_node=start_node,
            start_node_mec=start_node_mec
        )
        
        return Dijkstra.calculate_ETE_latency(
            previous_nodes=previous_nodes, 
            shortest_path=shortest_path, 
            start_node=start_node, 
            target_node=target_node
        )
        
    
    def get_shortest_path(mec_set: List['Mec'], graph: 'Graph', start_node: 'BaseStation'):
        """gets the shortest path from one node to all other nodes, where the weights are given in E2E latency"""
        #start_node_mec= ControllerInterface.MecController().get_mec(mec_set=mec_set, base_station=start_node)
        start_node_mec= mec.MecController.get_mec(mec_set, start_node)
        previous_nodes, shortest_path = Dijkstra.build_shortest_path(
            graph, start_node, start_node_mec
        )
        
        """sorts (ascendent) the shortest path dict into a list of tuples based on latency."""
        sorted_shortest_path = sorted(shortest_path.items(), key=operator.itemgetter(1))
        #print(f'\nshortest path from {start_node.name} to all other nodes!')
        #print(sorted_shortest_path)
        """The first element is the start node, then the weight is 0"""
        del sorted_shortest_path[0] # TODO: CHECK IF THIS IS RIGHT, IT SEEMS THE SERVICE CANNOT BE DEPLOYED WHERE THE USER IS CONNECTED TO IF THIS IS CALLED
        #print(sorted_shortest_path)
        #a = input('')
        return sorted_shortest_path
