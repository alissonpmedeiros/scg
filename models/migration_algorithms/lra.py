import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 

""" controller modules """
from controllers import mec_controller

"""LA migration module"""
from models.migration_algorithms.la import LA

"""other modules"""
from typing import Dict


class LRA(LA):
    """provides a network latency and resource-aware (LRA) service migration algorithm that considers the resources of the MECs before performing migrations"""
    
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

    def perform_migration(
        self,
        base_station_set: Dict[str,'BaseStation'],
        mec_set: Dict[str,'Mec'],
        hmds_set: Dict[str,'VrHMD'],
        graph: 'Graph',
        service: 'VrService'
    )-> bool:
        return super().perform_migration(base_station_set, mec_set, hmds_set, graph, service)

    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> 'Mec':
        """overrides the discover_mec method of the NetLatencyMigration class"""
        
        return mec_controller.MecController.discover_mec(
            base_station_set, mec_set, graph, start_node, service
        )
