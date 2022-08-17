import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 
    
from models.migration_ABC import Migration

""" controller modules """
from controllers import vr_controller 
from controllers import bs_controller 
from controllers import scg_controller 
from controllers import mec_controller
from controllers import dijkstra_controller 

"""other modules"""
from typing import Dict


class DSCP(Migration):
    """
    Behaviour of DSCP algorithm: given a service, find all possible combinations of base stations, MECs, and VR HMDs that can serve the service with the lowest latency
    1. Find the HMD b_i that hosts service f_m
    2. Compares b_i with all other MECs 
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

    

    
