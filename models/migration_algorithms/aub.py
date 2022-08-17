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


class AUB(Migration):
    """ implements the algorithm Average Utilization Based (AUB) Migration """

    """ 
    Describe the algorithm: 
    (i) SFCs should be placed on the paths where link latency is as optimal as possible; 
    (ii) processing capacity of VNFs can be improved to reduce response latency by allocating more resources to those VNFs. AUB only considers (ii), while SCG consider both. 
    
    1. Both under-utilized and over-utilized servers are first identified
    2. For each over-utilized server, one or more VNFs are selected as victim VNFs based on Eq. (20
    3. Afterwards, optimal servers are chosen from under-utilized servers for these victim VNFs using policy of choosing target server
    4.
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

    

    
