'''
"""graph module"""
from models.graph import Graph
from controllers.dijkstra_controller import DijkstraController
from controllers.mec_controller import MecController

"""vr modules"""
from models.vr import VrService, VrHMD
from controllers.vr_controller import VrController

"""mec modules"""
from models.mec import Mec 

"""migration module"""
from models.migration_ABC import Migration

"""base station modules"""
from models.base_station import BaseStation
from controllers.bs_controller import BaseStationController

"""other imports"""
from typing import List
import sys


class NetLatencyMigration(Migration):
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph):
        return super().check_services(
            base_station_set, mec_set, vr_users, graph
        )

    def service_migration(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService
    ) -> bool:
        return self.perform_migration(
            base_station_set=base_station_set,
            mec_set=mec_set,
            vr_users=vr_users,
            graph=graph,
            service=service,
        )

    def perform_migration(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """
        
        #service_bs_location = MecController.get_service_bs_location(
        #    base_station_set, mec_set, service.id
        #)
        
        
        service_owner = VrController.get_vr_service_owner(
            vr_users=vr_users, service=service
        )
        mec_candidate = self.discover_mec(
            base_station_set=base_station_set,
            mec_set=mec_set,
            user=service_owner,
            service=service,
            graph=graph
        )
        
        if mec_candidate.id is not None and MecController.check_deployment(
                mec_set, mec_candidate, service
            ):
            service_mec_server = MecController.get_service_mec_server(
                mec_set, service.id
            )
            extracted_service = MecController.remove_service(
                service_mec_server, service
            )
            MecController.deploy_service(
                mec_candidate, extracted_service
            )
            self.successful_migrations += 1
            return True
        else:
            self.unsuccessful_migrations += 1
            return False

            
    def discover_mec(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], user: VrHMD, graph: Graph, service: VrService,
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
            
            aux_path, new_latency = DijkstraController.get_ETE_latency(
                mec_set=mec_set,
                graph=graph,
                start_node=current_base_station.id,
                target_node=base_station.id
            )

            if new_latency <= shortest_latency:
                path = aux_path
                shortest_latency = new_latency

        """ we need to take care of the case where there is no more mec available """
        if not path:
            return None

        # print(" -> ".join(path))
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )
        return bs_destination.mec_id

'''