import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 

""" SCG class module """    
from models.migration_algorithms.scg import SCG

""" controller modules """
from controllers import bs_controller 
from controllers import mec_controller
from controllers import dijkstra_controller 

"""other modules"""
from typing import Dict


class DSCP(SCG):
    
    """
    The DSCP is a combinational optimization problem consisting of finding the optimal service placement of a service chain $s_n$ with $n$ services $f_m$ such that the E2E latency of $s_n$ does not exceed 5ms. To achieve such latency, a backtracking algorithm is required to efficiently solve DSCP since it is required to search the combination of the optimal service placement to meet the acceptable E2E latency over $B^*$ (allocation vectors including MECs and HMDs), $W^*$ (set of all possible maximum data throughput), $P^*_n$ (computing latency of each allocation vector), and $K^*_n$ (network latency) whenever the latency exceeds the acceptable E2E latency. 
    
    DSCP class inherits all methods from SCG. However, DSCP class overrides the mec_discover method from SCG class at this new method does not use the zones concept to optimize the search to achieve a latency of 5ms.
    """
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph'
    ) -> None:
        return super().check_services(base_station_set, mec_set, hmds_set, graph)

    def service_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'],  
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return super().service_migration(base_station_set, mec_set, hmds_set, graph, service)
    
    def offload_service(
        self, mec_candidate: 'Mec', 
        hmd: 'VrHMD', 
        service: 'VrService'
    ):
        return super().offload_service(mec_candidate, hmd, service)
    
    def reverse_offloading(
        self, 
        mec_set: Dict[str, 'Mec'], 
        hmds_set: Dict[str, 'VrHMD'], 
        hmd_ip: str, 
        service: 'VrService'
    ) -> bool:
        return super().reverse_offloading(mec_set, hmds_set, hmd_ip, service)
    
    def perform_migration(
        self, 
        mec_set: Dict[str, 'Mec'], 
        mec_candidate: 'Mec', 
        current_target_node: 'BaseStation', 
        service: 'VrService'
    ) -> bool:
        return super().perform_migration(mec_set, mec_candidate, current_target_node, service)

    
    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> Dict[str,'Mec']:
        """ discovers a MEC server for a VR service """ 
        #print(f'*** Discovering MEC ***')
        
        """here, the parameter zones is not set, then the algorithm will find out all posibilities"""
        shortest_path = dijkstra_controller.DijkstraController.get_ETE_shortest_path(
            mec_set, graph, start_node
        )
        
        mec_dict: Dict[str,'Mec'] = {
            'id': None,
            'mec': None
        }
        
        # Iterate over the sorted shortest path (list of tuples) and checks whether a mec server can host the service
        for node in shortest_path:    
            bs_name = node[0]
            bs =  bs_controller.BaseStationController.get_base_station_by_name(base_station_set, bs_name)
            base_station: BaseStation = bs.get('base_station')
            
            bs_mec = mec_controller.MecController.get_mec(
                mec_set, base_station
            )
            
            if mec_controller.MecController.check_deployment(bs_mec, service):
                mec_dict.update({'id': base_station.mec_id, 'mec': bs_mec})
                break
            
        
        #print(shortest_path)
        if mec_dict.get('mec') is None:
            print(f'\nALL MEC servers are overloaded! Discarting...')
            
        return mec_dict

    
    def trade_off(
        self, 
        base_station_set: Dict[str, 'BaseStation'], 
        mec_set: Dict[str, 'Mec'], 
        hmds_set: Dict[str, 'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return super().trade_off(base_station_set, mec_set, hmds_set, graph, service)