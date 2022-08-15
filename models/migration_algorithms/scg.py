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

"""other imports"""
import sys
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class SCG(Migration):
    # TODO: refact alpha scheme!
    alpha: int = 0
    alpha_max_threshold = 1719
    alpha_with_experiment: bool = False   
    total_services_migrated: int = field(init=False)
    
    def __post_init__(self):
        self.total_services_migrated = self.alpha * self.alpha_max_threshold

    def check_services(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph'
    ) -> None:
        return super().check_services(base_station_set, mec_set, hmds_set, graph)

    def get_migrations(self) -> dict:
        return super().get_migrations()
        

    def service_migration(
        self, base_station_set: List['BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return self.trade_off(base_station_set, mec_set, hmds_set, graph, service)
    
    def offload_service(
        self, mec_candidate: 'Mec', hmd: 'VrHMD', service: 'VrService'
    ):
        """ offloads a vr service from HDM to MEC server """
        #print("*** Performing offloading ***")
        
        extracted_service = vr_controller.VrController.remove_vr_service(hmd, service.id)

        mec_controller.MecController.deploy_service(mec_candidate, extracted_service)
        self.successful_migrations +=1    
        return True
        
    def reverse_offloading(
        self, mec_set: Dict[str,'Mec'], hmds_set: Dict[str,'VrHMD'], hmd_ip: str, service: 'VrService'
    ) -> bool:
        """ offloads a service i back to vr hmd """
        #print("*** Performing reverse offloading ***")

        service_mec_server_id, service_mec_server = mec_controller.MecController.get_service_mec_server(
            mec_set, service.id
        )
        extracted_service = mec_controller.MecController.remove_service(
            service_mec_server, service
        )

        vr_controller.VrController.deploy_vr_service(
            hmds_set, hmd_ip, extracted_service
        )
        
        self.successful_migrations +=1
        return True
    
    def perform_migration(
        self, 
        mec_set: Dict[str,'Mec'], 
        mec_candidate: 'Mec', 
        current_target_node: 'BaseStation', 
        service: 'VrService'
    ) -> bool:        
        """provides the service migration based on the current distance between a hmd and where the service is deployed"""
            
        current_target_node_mec = mec_controller.MecController.get_mec(
            mec_set, current_target_node
        )
        extracted_service = mec_controller.MecController.remove_service(
            current_target_node_mec, service
        )
        
        mec_controller.MecController.deploy_service(
            mec_candidate, extracted_service
        )
        #print("*** Performing migration ***")
        
        
        #print(f'service {service.id} moved from MEC {current_target_node_mec.name} to {mec_candidate.name}')
        self.successful_migrations +=1
        return True
        

    #TODO: For this method, we have to implement some sort of penality to count when the service is 
    # deployed in a mec that has lower latency than its current mec server however it is higher than 5ms.
    
    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> 'Mec':
        """ discovers a MEC server for a VR service """ 
        #print(f'*** Discovering MEC ***')
    
        shortest_path = dijkstra_controller.DijkstraController.get_shortest_path(
            mec_set, graph, start_node
        )
        # Iterate over the sorted shortest path (list of tuples) and checks whether a mec server can host the service
        for node in shortest_path:    
            bs_name = node[0]
            bs_id, base_station = bs_controller.BaseStationController.get_base_station_by_name(
                base_station_set, bs_name
            )
            bs_mec = mec_controller.MecController.get_mec(
                mec_set, base_station
            )
            
            if mec_controller.MecController.check_deployment(bs_mec, service):
                return base_station.mec_id, bs_mec
            
        
        print(shortest_path)
        print(f'\nALL MEC servers are overloaded! Discarting...')
        a = input('')
        return None, None
        
        
    #TODO: we have to implement the restriction of 5ms before migrating a service.admin 
    def trade_off(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""
        #print(f'\n___________________________________________________\n')
        #print(f'\n*** checking service {service.id} ***\n')
        
        service_owner_id, service_owner = vr_controller.VrController.get_vr_service_owner(
            hmds_set, service
        )
        
        # initializing the node where the hmd in connnected to 
        start_node = bs_controller.BaseStationController.get_base_station(
            base_station_set, service_owner.current_location
        )
        
        # initializing the candidate node
        mec_candidate_id, mec_candidate = self.discover_mec(
            base_station_set, mec_set, graph, start_node, service
        )
        
        candidate_target_node = mec_controller.MecController.get_mec_bs_location(
            base_station_set, mec_candidate_id
        )
        
        candidate_latency = scg_controller.ScgController.get_E2E_latency(
            mec_set, graph, start_node, candidate_target_node
        )

        candidate_service_latency = candidate_latency.get('e2e_latency')
        
        
        hmd_latency = vr_controller.VrController.get_hmd_latency(
            base_station_set, service_owner
        )
        
        
        if any(service.id == hmd_service.id for hmd_service in service_owner.services_set):
            """ checks whether a service IS deployed on the HMD """
            
            
            if mec_candidate is None:
                #TODO: Migration should be considered. However, there are no mec servers available. 
                #The service stays on the HMD. We should consider a service migration violation... 

                #print('*** Cannot perform migration, there is no MEC available in the infrastructure ***')
                self.unsuccessful_migrations +=1
                return False    
            
            
            
            elif candidate_service_latency < hmd_latency:
                return self.offload_service(mec_candidate, service_owner, service)

            else:
                # cannot find out a MEC server with lower latency than the HMD. 
                # this means a violation of the service migration policy.
                #print(f'\n*** Violation of service migration policy ***\n')
                self.unsuccessful_migrations +=1
                return False    
                
            

        else:
            """ otherwise, the service is deployed on MEC servers"""
            
            current_target_node = mec_controller.MecController.get_service_bs(
                base_station_set, mec_set, service.id
            )
            
            
            current_latency = scg_controller.ScgController.get_E2E_latency(
                mec_set, graph, start_node, current_target_node
            )
            
            current_service_latency = current_latency.get('e2e_latency')
            
            #print(f'service is deployed on MEC {current_target_node.name}')
            #print(f'Latencies: hmd: {hmd_latency} | current: {current_service_latency} | candidate: {candidate_service_latency}\n')
            
            if mec_candidate is None:
                candidate_service_latency = sys.maxsize
                
            if current_service_latency > hmd_latency or current_service_latency > candidate_service_latency:
                if hmd_latency < candidate_service_latency:
                    return self.reverse_offloading(mec_set, hmds_set, service_owner_id, service)
                return self.perform_migration(mec_set, mec_candidate, current_target_node, service)

            
            
            # TODO: FIND OUT A WAY TO IMPLEMENT ALPHA IN A PROPPER WAY HERE.
            '''else:
                services_on_hmds = scg.ScgController.get_vr_services_on_HMD(vr_users)
                # TODO: ALPHA is being implemented here. Implement the case where ALPHA is 0 and 1. If 0, then just use the migrate. Otherwise, use the trade-off analysis witht the HMD
                if not self.alpha_with_experiment:
                    # Returning perform_migration due to energy consumption measurements
                    print(f'\ncurrent service latency: {current_service_latency}' + f' | hmd latency: {hmd_latency}\n')
                    return self.reverse_offloading(
                            mec_set=mec_set,
                            vr_users=vr_users,
                            user=service_owner,
                            service=service,
                        )
                elif self.alpha == 0: # TODO: CHECK THIS PROCEDURE, BECAUSE ITS CALLING MIGRATION AGAIN
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
                        )'''
        
                 
        
    

    