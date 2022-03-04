"""graph module"""
from graph.graph import Graph
from graph.dijkstra import DijkstraController

"""vr modules"""
from vr.vr_hmd import VrHMD
from vr.vr_service import VrService
from vr.vr_controller import VrController

"""mec modules"""
from mec.mec import Mec 
from mec.mec_agent import MecAgent
from mec.mec_controller import MecController

"""migration module"""
from migration.algorithms.scg_tradeoff import SCG 

"""react algorithm modules"""
from migration.react.react_algorithm import REACTApproach

"""base station modules"""
from base_station.base_station import BaseStation
from base_station.bs_controller import BaseStationController

"""scg controller module"""
from scg_controller.scg_controller import ScgController

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
        mec_id_candidate = None
        path = []
        for base_station in base_station_set:
            """ 
            tests if the base station is not the source base station and the mec 
            attached to the base station instance can deploy the service  
            """
            src_bs = BaseStationController.get_base_station(
                base_station_set, current_base_station.id
            )
            src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
            aux_path, new_latency = DijkstraController.get_shortest_path(
                start_node=current_base_station.id,
                start_node_computing_delay=src_mec.computing_latency,
                start_node_wireless_delay=src_bs.wireless_latency,
                target_node=base_station.id,
                graph=graph
            )

            if new_latency <= shortest_latency:
                path = aux_path
                shortest_latency = new_latency
                mec_id_candidate = base_station.mec_id
            
        """ we need to take care of the case where there are no more mec available """
        if not path:
            return None
        
        if not (
            MecAgent.check_deployment(
                mec_set, mec_id_candidate, service
            )
        ):
            #print('REACT ENABLED!')
            REACTApproach.solidarity(
                mec_set=mec_set, 
                mec_id=mec_id_candidate, 
                service=service, 
                sucessful_migrations=self.successful_migrations, 
                unsuccessful_migrations=self.unsuccessful_migrations
            )
        
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )
        return bs_destination.mec_id