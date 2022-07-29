import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.graph import Graph
    from models.base_station import BaseStation 
    
""" other modules """
import sys

class Dijkstra:
    @staticmethod
    def build_shortest_path(graph: 'Graph', start_node: 'BaseStation', start_node_mec: 'Mec'):
        unvisited_nodes = list(graph.get_nodes())
        """
        We'll use this dict to save the cost of visiting each node and update it as we move along the graph. 
        This variable is similar to dist in the standard Dijkstra's algorithm.
        """   
        dist = {}
    
        """We'll use this dict to save the shortest known path to a node found so far"""
        previous_nodes = {}
    
        """We'll use max_value to initialize the "infinity" value of the unvisited nodes"""   
        max_value = sys.maxsize
        for node in unvisited_nodes:
            dist[node] = max_value
            
        """However, we initialize the  starting node with wireless latency of the Base station to reach the attached MEC and the computing latency of the MEC """   
        dist[start_node.name] = start_node.wireless_latency + start_node_mec.computing_latency  
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
                if current_min_node == None:
                    current_min_node = node
                elif dist[node] < dist[current_min_node]:
                    current_min_node = node
            #pprint(dist)
            #print(f'\ncurrent min node: {current_min_node} -> {dist[current_min_node]}\n')
              
            """The code block below retrieves the current node's neighbors and updates their distances"""
            neighbors = graph.get_outgoing_edges(current_min_node)
            #pprint(neighbors) 
            #print('\n')
            for neighbor in neighbors:
                #tentative_value = dist[current_min_node] + graph.get_network_latency(current_min_node, neighbor)
                #print(f'current tentative value: {tentative_value}')
                #tentative_value = (dist[current_min_node] - w_p[current_min_node]) + graph.value(current_min_node, neighbor) + w_p[neighbor]
                tentative_value = (dist[current_min_node] - graph.get_node_computing_latency(current_min_node) + graph.get_network_latency(current_min_node, neighbor) + graph.get_node_computing_latency(neighbor))
                #print(f'new tentative value: {tentative_value}')
                #print(f'from {current_min_node} -> {neighbor}: [{round(dist[current_min_node] - graph.get_node_computing_latency(current_min_node), 2)}] + [{graph.get_network_latency(current_min_node, neighbor)}] + [{graph.get_node_computing_latency(neighbor)}] = {tentative_value}')
                #a = input('')
                if tentative_value < dist[neighbor]:
                    dist[neighbor] = tentative_value
                    """We also update the best path to the current node"""
                    previous_nodes[neighbor] = current_min_node
                    #print(f'*** chosen neighbor: {dist[neighbor]}')
                    
            #a = input('')
            """After visiting its neighbors, we mark the node as 'visited'"""
            unvisited_nodes.remove(current_min_node)
        return previous_nodes, dist
    
    @staticmethod
    def calculate_ETE_latency( 
        previous_nodes, shortest_path, start_node: 'BaseStation', target_node: 'BaseStation'
    ):
        """ returns the shortest path (lowest ETE latency) between the source and destination node and the path cost """
        if not target_node:
            print(f'\ntarget node is None within Dijkstra.calculate_ETE_latency()')
            a = input('')
        path = []
        node = target_node.name
        
        while node != start_node.name:
            path.append(node)
            node = previous_nodes[node]
    
        """ Adds the start node manually """
        path.append(start_node.name)
        
        #print(f'we found the following best path from {start_node.name} with a value of {shortest_path[target_node.name]}')
        #print(" -> ".join(reversed(path)))
        #a = input('')
        path.reverse()
        return path, shortest_path[target_node.name]

















