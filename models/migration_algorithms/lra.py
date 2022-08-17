import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 

""" controller modules """
from controllers import bs_controller 
from controllers import mec_controller
from controllers import dijkstra_controller 

"""LA migration module"""
from models.migration_algorithms.la import LA

"""other modules"""
from typing import Dict


class LRA(LA):
    """
    provides a network latency and resource-aware (LRA) service migration 
    algorithm that considers the resources of the MECs before performing migrations
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

    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> Dict[str,'Mec']:
        """ discovers a nearby MEC server to either offload or migrate the service considering the resource availaiblity of MEC nodes"""
        
        mec_dict: Dict[str, Mec] = {
            'id': None,
            'mec': None
        }   
        
        shortest_path = dijkstra_controller.DijkstraController.get_shortest_path(
            mec_set, graph, start_node
        )
        # Iterate over the sorted shortest path (list of tuples) and checks whether a mec server can host the service
        for node in shortest_path:    
            bs_name = node[0]
            bs =  bs_controller.BaseStationController.get_base_station_by_name(base_station_set, bs_name)
            base_station: BaseStation = bs.get('base_station')
            bs_mec = mec_controller.MecController.get_mec(mec_set, base_station)
            
            if mec_controller.MecController.check_deployment(bs_mec, service):
                mec_dict.update({'id': base_station.mec_id, 'mec': bs_mec})
                break
            
        if mec_dict.get('mec') is None:
            print(f'\nALL MEC servers are overloaded! Discarting...')
        
        return mec_dict

    def perform_migration(
        self,
        base_station_set: Dict[str,'BaseStation'],
        mec_set: Dict[str,'Mec'],
        hmds_set: Dict[str,'VrHMD'],
        graph: 'Graph',
        service: 'VrService'
    )-> bool:
        return super().perform_migration(base_station_set, mec_set, hmds_set, graph, service)