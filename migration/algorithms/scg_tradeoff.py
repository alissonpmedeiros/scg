"""graph module"""
from dataclasses import field
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
from migration.migration_ABC import Migration

"""base station modules"""
from base_station.base_station import BaseStation
from base_station.bs_controller import BaseStationController

"""scg controller module"""
from scg_controller.scg_controller import ScgController

"""other imports"""
from typing import List
from dataclasses import dataclass, field



@dataclass
class SCG(Migration):
    alpha: int = 0.5
    alpha_max_threshold = 1875
    alpha_with_experiment: bool = False   
    total_services_migrated: int = field(init=False)
    
    def __post_init__(self):
        self.total_services_migrated = self.alpha * self.alpha_max_threshold

    def check_services(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph):
        return super().check_services(base_station_set, mec_set, vr_users, graph)

    def get_migrations(self):
        return super().get_migrations()
        

    def service_migration(
        self,
        base_station_set: List[BaseStation],
        mec_set: List[Mec],
        vr_users: List[VrHMD], 
        graph: Graph,
        service: VrService,
    ) -> bool:
        return self.trade_off(
            base_station_set=base_station_set,
            mec_set=mec_set,
            vr_users=vr_users,
            graph=graph,
            service=service,
        )
        # TODO: sucessful migrations and unsuccessful migrations can be counted here based on the return value of the function. Consider refactoring it
    
    def offload_service(self, mec_set: List[Mec], mec_id_candidate: str, vr_users: List[VrHMD], service_owner_ip: str, service: VrService):
        """ offloads a vr service from HDM to MEC server """
        extracted_service = VrController.remove_vr_service(
            vr_users=vr_users,
            user_ip=service_owner_ip,
            service_id=service.id,
        )

        MecAgent.deploy_service(
            mec_set, mec_id_candidate, extracted_service
        )

    def trade_off(
        self, 
        base_station_set: List[BaseStation], 
        mec_set: List[Mec], 
        vr_users: List[VrHMD],
        graph: Graph,
        service: VrService,
    ) -> bool:
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""

        service_owner = VrController.get_vr_service_owner(
            vr_users=vr_users, service=service
        )
        
        if any(service.id == user_service.id for user_service in service_owner.services_set):
            """ checks whether a service IS deployed on the HMD """
            hmd_latency = VrController.get_hmd_latency(
                base_station_set=base_station_set,
                vr_users=vr_users,
                user_ip=service_owner.ip,
            )

            mec_id_candidate = self.discover_mec(
                base_station_set=base_station_set,
                mec_set=mec_set,
                user=service_owner,
                service=service,
                graph=graph
            )

            if mec_id_candidate is not None:
                mec_candidate_location = MecAgent.get_mec_bs_location(
                    base_station_set, mec_id_candidate
                )
                computing_latency, network_latency, new_service_latency = ScgController.get_E2E_latency(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    src_location=service_owner.current_location,
                    dst_location=mec_candidate_location,
                    graph=graph
                )

                if new_service_latency < hmd_latency:
                    #print("*** Performing offloading ***")
                    self.offload_service(mec_set, mec_id_candidate, vr_users, service_owner.ip, service)
                    self.successful_migrations +=1
                    
                return True

            else:
                """
                Migration should be considered. However, there are no mec servers available. 
                The service stays on the HMD. 
                We should consider a service migration violation... 
                """
                self.unsuccessful_migrations +=1
                return False

        else:
            """ otherwise, the service is deployed on MEC servers"""
            service_location = MecAgent.get_service_bs_id(
                base_station_set, mec_set, service.id
            )

            """ 
            measures the latency between bs where the user 
            is connected and the mec where the service is deployed 
            """
           
            computing_latency, network_latency, current_service_latency = ScgController.get_E2E_latency(
                base_station_set=base_station_set,
                mec_set=mec_set,
                src_location=service_owner.current_location,
                dst_location=service_location,
                graph=graph
            )

            hmd_latency = VrController.get_hmd_latency(
                base_station_set=base_station_set,
                vr_users=vr_users,
                user_ip=service_owner.ip,
            )


            if current_service_latency <= hmd_latency:
                return self.perform_migration(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    user=service_owner,
                    graph=graph,
                    service=service
                )
            else:
                #print("*** Performing reverse offloading ***")
                services_on_hmds = ScgController.get_vr_services_on_HMD(vr_users)
                # TODO: ALPHA is being implemented here. Implement the case where ALPHA is 0 and 1. If 0, then just use the migrate. Otherwise, use the trade-off analysis witht the HMD
                if not self.alpha_with_experiment:
                    # Returning perform_migration due to energy consumption measurements
                    return self.reverse_offloading(
                            mec_set=mec_set,
                            vr_users=vr_users,
                            user=service_owner,
                            service=service,
                        )
                elif self.alpha == 0:
                    # No HMDs are considered
                    return self.perform_migration(
                            base_station_set=base_station_set,
                            mec_set=mec_set,
                            user=service_owner,
                            graph=graph,
                            service=service
                        )
                else:
                    # If ALPHA experiments is enabled, then we check the maximum services deployed on the HMD.
                    if services_on_hmds < self.total_services_migrated:
                        return self.reverse_offloading(
                            mec_set=mec_set,
                            vr_users=vr_users,
                            user=service_owner,
                            service=service,
                        )
                    else:
                        return self.perform_migration(
                            base_station_set=base_station_set,
                            mec_set=mec_set,
                            user=service_owner,
                            graph=graph,
                            service=service
                        )
                
                    
        
    
    def reverse_offloading(
        self, 
        mec_set: List[Mec], 
        vr_users: List[VrHMD], 
        user: VrHMD, 
        service: VrService
    ) -> bool:
        """ offloads a service i back to vr hmd """

        service_server_id = MecAgent.get_service_server_id(mec_set, service.id)
        extracted_service = MecAgent.remove_service(
            mec_set, service_server_id, service.id
        )

        VrController.deploy_vr_service(
            vr_users=vr_users, user_ip=user.ip, service=extracted_service
        )
        
        self.successful_migrations +=1
        return True
    
    def perform_migration(
        self,
        base_station_set: List[BaseStation],
        mec_set: List[Mec],
        user: VrHMD,
        graph: Graph,
        service: VrService, 
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """
        

        service_server_id = MecAgent.get_service_server_id(mec_set, service.id)
        service_location = MecAgent.get_service_bs_id(
            base_station_set, mec_set, service.id
        )
        computing_latency, network_latency, previous_service_latency = ScgController.get_E2E_latency(
            base_station_set=base_station_set,
            mec_set=mec_set,
            graph=graph,
            src_location=user.current_location,
            dst_location=service_location,
        )

        mec_id_candidate = self.discover_mec(
            base_station_set=base_station_set,
            mec_set=mec_set,
            graph=graph,
            user=user,
            service=service,
        )

        if mec_id_candidate is not None:
            mec_candidate_location = MecAgent.get_mec_bs_location(
                base_station_set, mec_id_candidate
            )
            computing_latency, network_latency, new_service_latency = ScgController.get_E2E_latency(
                base_station_set=base_station_set,
                mec_set=mec_set,
                src_location=user.current_location,
                dst_location=mec_candidate_location,
                graph=graph
            )

            if new_service_latency < previous_service_latency:
                extracted_service = MecAgent.remove_service(
                    mec_set, service_server_id, service.id
                )
                MecAgent.deploy_service(mec_set, mec_id_candidate, extracted_service)
                #print("*** Performing migration ***")
                # print("service {} move from MEC {} to {}".format(service_id, service_server_id, mec_id_candidate))
                # print("new latency: {}\n".format(new_service_latency))
                self.successful_migrations +=1
            return True

        else:
            #print("*** Migration failed. Error: no candidates ***")
            self.unsuccessful_migrations +=1
            return False

    
    

    def discover_mec(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], graph: Graph, user: VrHMD, service: VrService
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            if ( 
                MecAgent.check_deployment(
                    mec_set, base_station.mec_id, service
                )
            ):
                """ tests if the mec attached to the base station can deploy the service"""
                src_bs = BaseStationController.get_base_station(
                    base_station_set, user.current_location
                )
                src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
                aux_path, new_latency = DijkstraController.get_shortest_path(
                    start_node=user.current_location,
                    start_node_computing_delay=src_mec.computing_latency,
                    start_node_wireless_delay=src_bs.wireless_latency,
                    target_node=base_station.id,
                    graph=graph,
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