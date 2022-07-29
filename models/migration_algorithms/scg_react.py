'''"""graph module"""
from models.graph import Graph
from controllers.dijkstra_controller import DijkstraController

"""vr modules"""
from models.vr import VrService, VrHMD
from controllers.vr_controller import VrController

"""mec modules"""
from models.mec import Mec 
from controllers.mec_controller import MecController

"""migration module"""
from models.migration_algorithms.scg_tradeoff import SCG 

"""react algorithm modules"""
from models.migration_algorithms.react_algorithm import REACTApproach

"""base station modules"""
from models.base_station import BaseStation
from controllers.bs_controller import BaseStationController

"""scg controller module"""
from controllers.scg_controller import ScgController

"""other imports"""
from typing import List


class ScgReact(SCG):
    """inherited from the SCG class"""
    def check_services(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph):
        return super().check_services(base_station_set, mec_set, vr_users, graph)

    """inherited from the SCG class"""
    def get_migrations(self):
        return super().get_migrations()

    """inherited from the SCG class"""
    def service_migration(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService
    ) -> bool:
        return super().service_migration(base_station_set, mec_set, vr_users, graph, service)

    """inherited from the SCG class"""
    def reverse_offloading(
        self, mec_set: List[Mec], vr_users: List[VrHMD], user: VrHMD, service: VrService
    ) -> bool:
        return super().reverse_offloading(mec_set, vr_users, user, service)

    """inherited from the SCG class"""
    def perform_migration(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], user: VrHMD, graph: Graph, service: VrService
    ) -> bool:
        return super().perform_migration(base_station_set, mec_set, user, graph, service)

    """inherited from the SCG class"""
    def trade_off(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService
    ) -> bool:
        return super().trade_off(base_station_set, mec_set, vr_users, graph, service)

    """this method is not inherited from the SCG class, we rewrote it"""
    def discover_mec(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], user: VrHMD, graph: Graph, service: VrService
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        shortest_latency = float("inf")
        mec_candidate = None
        path = []
        for base_station in base_station_set:
            """ 
            tests if the base station is not the source base station and the mec 
            attached to the base station instance can deploy the service  
            """
            #src_bs = BaseStationController.get_base_station(
            #    base_station_set, current_base_station.id
            #)
            #src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
            
            aux_path, new_latency = DijkstraController.get_ETE_latency(
                mec_set=mec_set,
                graph=graph,
                start_node=current_base_station.id,
                target_node=base_station.id
            )

            if new_latency <= shortest_latency:
                path = aux_path
                shortest_latency = new_latency
                mec_candidate = MecController.get_mec(mec_set, base_station.mec_id)
            
        """ we need to take care of the case where there are no more mec available """
        if not path:
            return None
        
        if not (
            MecController.check_deployment(
                mec_set, mec_candidate, service
            )
        ):
            #print('REACT ENABLED!')
            REACTApproach.solidarity(
                mec_set=mec_set, 
                mec_id=mec_candidate, 
                service=service, 
                sucessful_migrations=self.successful_migrations, 
                unsuccessful_migrations=self.unsuccessful_migrations
            )
        
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )
        return bs_destination.mec_id'''