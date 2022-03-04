import sys
from graph.graph import Graph

class Dijkstra:
    """ represents the Dijkstra algorithm """
    @staticmethod
    def dijkstra_algorithm(graph: Graph, start_node: str, start_node_computing_delay:float, start_node_wireless_delay: float ):
        unvisited_nodes = list(graph.get_nodes())
    
        """We'll use this dict to save the cost of visiting each node and update it as we move along the graph"""   
        shortest_path = {}
    
        """We'll use this dict to save the shortest known path to a node found so far"""
        previous_nodes = {}
    
        """We'll use max_value to initialize the "infinity" value of the unvisited nodes"""   
        max_value = sys.maxsize
        for node in unvisited_nodes:
            shortest_path[node] = max_value
        """However, we initialize the starting node's value with its computing_delay and the wireless latency of the bs associated to the starting node (mec)"""   
        shortest_path[start_node] = start_node_computing_delay + start_node_wireless_delay
        
        """The algorithm executes until we visit all nodes"""
        while unvisited_nodes:
            """The code block below finds the node with the lowest score"""
            current_min_node = None
            for node in unvisited_nodes: 
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
        #print(f'latency: {shortest_path[target_node]}')
        #a = input('')
        path.reverse()
        return path, shortest_path[target_node]


class DijkstraController:
        """ represents the Dijkstra controller to get the shortest path"""        
        def get_shortest_path(
            start_node: str,
            start_node_computing_delay: float, 
            start_node_wireless_delay: float,
            target_node: str,
            graph: Graph,
        ):
            previous_nodes, shortest_path = Dijkstra.dijkstra_algorithm(
                graph=graph, 
                start_node=start_node,
                start_node_computing_delay=start_node_computing_delay,
                start_node_wireless_delay=start_node_wireless_delay,
            )

            return Dijkstra.get_result(
                previous_nodes, 
                shortest_path, 
                start_node=start_node, 
                target_node=target_node)


    