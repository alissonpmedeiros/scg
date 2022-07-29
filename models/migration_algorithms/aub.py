

""" model modules"""
#if TYPE_CHECKING:
from models import Mec as Mec
from models import VrHMD as VrHMD
from models import VrService as VrService
from models import Migration as Migration
from models import BaseStation as BaseStation



"""other imports"""
from typing import List


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
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD]
    ):
        return super().check_services(base_station_set, mec_set, vr_users)
    
    
    def service_migration(
        self, 
        base_station_set: List[BaseStation], 
        mec_set: List[Mec], 
        vr_users: List[VrHMD],
        service: VrService,
    ):
        pass