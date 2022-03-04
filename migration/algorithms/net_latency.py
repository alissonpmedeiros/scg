"""graph module"""
from graph.graph import Graph

"""vr modules"""
from vr.vr_hmd import VrHMD
from vr.vr_service import VrService
from vr.vr_controller import VrController

"""mec modules"""
from mec.mec import Mec 
from mec.mec_agent import MecAgent

"""migration module"""
from migration.migration_ABC import Migration

"""base station modules"""
from base_station.base_station import BaseStation
from base_station.bs_controller import BaseStationController

"""other imports"""
from typing import List
import sys


class NetLatencyMigration(Migration):
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph):
        return super().check_services(
            base_station_set, mec_set, vr_users, graph
        )

    def service_migration(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService
    ) -> bool:
        return self.perform_migration(
            base_station_set=base_station_set,
            mec_set=mec_set,
            vr_users=vr_users,
            graph=graph,
            service=service,
        )

    def perform_migration(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """
        '''
        service_bs_location = MecAgent.get_service_bs_location(
            base_station_set, mec_set, service.id
        )
        '''
        
        service_owner = VrController.get_vr_service_owner(
            vr_users=vr_users, service=service
        )
        mec_id_candidate = self.discover_mec(
            base_station_set=base_station_set,
            mec_set=mec_set,
            user=service_owner,
            service=service,
            graph=graph
        )
        
        if mec_id_candidate is not None and MecAgent.check_deployment(
                mec_set, mec_id_candidate, service
            ):
            service_server_id = MecAgent.get_service_server_id(
                mec_set, service.id
            )
            extracted_service = MecAgent.remove_service(
                mec_set, service_server_id, service.id
            )
            MecAgent.deploy_service(
                mec_set, mec_id_candidate, extracted_service
            )
            self.successful_migrations += 1
            return True
        else:
            self.unsuccessful_migrations += 1
            return False

            
    def discover_mec(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], user: VrHMD, graph: Graph, service: VrService,
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
            aux_path, new_latency = DijkstraController.get_shortest_path(
                start_node=current_base_station.id,
                target_node=base_station.id,
                graph=graph
            )

            if new_latency <= shortest_latency:
                path = aux_path
                shortest_latency = new_latency

        """ we need to take care of the case where there is no more mec available """
        if not path:
            return None

        # print(" -> ".join(path))
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )
        return bs_destination.mec_id





class Dijkstra:

    @staticmethod
    def dijkstra_algorithm(graph: Graph, start_node):
        unvisited_nodes = list(graph.get_nodes())
    
        """We'll use this dict to save the cost of visiting each node and update it as we move along the graph"""   
        shortest_path = {}
    
        """We'll use this dict to save the shortest known path to a node found so far"""
        previous_nodes = {}
    
        """We'll use max_value to initialize the "infinity" value of the unvisited nodes"""   
        max_value = sys.maxsize
        for node in unvisited_nodes:
            shortest_path[node] = max_value
        """However, we initialize the starting node's value with 0"""   
        shortest_path[start_node] = 0
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: # Iterate over the nodes
                if current_min_node == None:
                    current_min_node = node
                elif shortest_path[node] < shortest_path[current_min_node]:
                    current_min_node = node
                    
            """The code block below retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges(current_min_node)
            for neighbor in neighbors:
                tentative_value = shortest_path[current_min_node] + graph.value(current_min_node, neighbor)
                if tentative_value < shortest_path[neighbor]:
                    shortest_path[neighbor] = tentative_value
                    """We also update the best path to the current node"""
                    previous_nodes[neighbor] = current_min_node
    
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_min_node)
        
        return previous_nodes, shortest_path

    @staticmethod
    def get_result(
        previous_nodes, 
        shortest_path, 
        start_node, 
        target_node):
        """ returns the shortest path between the source and destination node and the path cost """

        path = []
        node = target_node
        
        while node != start_node:
            path.append(node)
            node = previous_nodes[node]
    
        """Add the start node manually"""
        path.append(start_node)
        
        #print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
        #print(" -> ".join(reversed(path)))
        path.reverse()
        return path, shortest_path[target_node]


class DijkstraController:
    @staticmethod
    def get_shortest_path(
        start_node: str, 
        target_node: str,
        graph: Graph, 
    ):
        
        previous_nodes, shortest_path = Dijkstra.dijkstra_algorithm(
            graph=graph, 
            start_node=start_node)

        return Dijkstra.get_result(
            previous_nodes, 
            shortest_path, 
            start_node=start_node, 
            target_node=target_node)
