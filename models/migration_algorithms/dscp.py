from models import Mec as Mec
from models import Graph as Graph
from models import VrHMD as VrHMD
from models import VrService as VrService
from models import Migration as Migration
from models import BaseStation as BaseStation

import controllers

"""other imports"""
from typing import List
from dataclasses import dataclass


@dataclass
class DSCP(Migration):

    """
    This class implements the DSCP algorithm for finding the optimal placement of a service giving a set 
    of base stations, MECs, and VR users, where the service is placed according to latency restrictions
    """

    #inherited from Migration
    def check_services(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph):
        return super().check_services(base_station_set, mec_set, vr_users, graph)

    #inherited from Migration
    def get_migrations(self):
        return super().get_migrations()
    
    #inherited from Migration
    def service_migration(
        self,
        base_station_set: List[BaseStation],
        mec_set: List[Mec],
        vr_users: List[VrHMD], 
        graph: Graph,
        service: VrService,
    ) -> bool:
        return self.find_optimal(
            base_station_set=base_station_set,
            mec_set=mec_set,
            vr_users=vr_users,
            graph=graph,
            service=service,
        )
        # TODO: sucessful migrations and unsuccessful migrations can be counted here based on the return value of the function. Consider refactoring it
        
    def find_optimal(base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService) -> bool:
        """
        Behaviour of DSCP algorithm: given a service, find all possible combinations of base stations, MECs, and VR HMDs that can serve the service with the lowest latency
        1. Find the HMD b_i that hosts service f_m
        2. Compares b_i with all other MECs 
        """
        
        service_owner = controllers.VrController.get_vr_service_owner(vr_users, service)
        owner_hmd_latency = service_owner.computing_latency
        
        
        
        return True
    
    
    
