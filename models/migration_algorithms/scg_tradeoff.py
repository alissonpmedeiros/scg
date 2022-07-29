import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.graph import Graph 
    from models.vr import VrHMD 
    from models.vr import VrService 
    from models.base_station import BaseStation 

from models.migration_ABC import Migration

""" controller modules """
from controllers import vr_controller as vr
from controllers import bs_controller as bs
from controllers import scg_controller as scg
from controllers import mec_controller as mec
from controllers import dijkstra_controller as dijkstra

"""other imports"""
import sys
from typing import List
from dataclasses import dataclass, field
from pprint import pprint as pprint


#TODO: WE SHOULD EXPECT LESS SERVICES DEPLOYED ON THE HMD...
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
        base_station_set: List['BaseStation'], 
        mec_set: List['Mec'], 
        vr_users: List['VrHMD'], 
        graph: 'Graph'
    ):
        return super().check_services(base_station_set, mec_set, vr_users, graph)

    def get_migrations(self):
        return super().get_migrations()
        

    def service_migration(
        self, base_station_set: List['BaseStation'], 
        mec_set: List['Mec'], 
        vr_users: List['VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return self.trade_off(base_station_set, mec_set, vr_users, graph, service)
    
    def offload_service(
        self, mec_candidate: 'Mec', vr_users: List['VrHMD'], vr_hmd: 'VrHMD', service: 'VrService'
    ):
        """ offloads a vr service from HDM to MEC server """
        #print("*** Performing offloading ***")
        
        extracted_service = vr.VrController.remove_vr_service(vr_hmd, service.id)

        mec.MecController.deploy_service(mec_candidate, extracted_service)
        self.successful_migrations +=1    
        return True
        
    def reverse_offloading(
        self, mec_set: List['Mec'], vr_users: List['VrHMD'], user: 'VrHMD', service: 'VrService'
    ) -> bool:
        """ offloads a service i back to vr hmd """
        #print("*** Performing reverse offloading ***")

        service_mec_server = mec.MecController.get_service_mec_server(mec_set, service.id)
        extracted_service = mec.MecController.remove_service(service_mec_server, service)

        vr.VrController.deploy_vr_service(vr_users, user.ip, extracted_service)
        
        self.successful_migrations +=1
        return True
    
    def perform_migration(
        self, mec_set: List['Mec'], mec_candidate: 'Mec', current_target_node: 'BaseStation', service: 'VrService'
    ) -> bool:        
        """provides the service migration based on the current distance between a hmd and where the service is deployed"""
        if not mec_candidate:
            #print('*** Cannot perform migration, there is no MEC available in the infrastructure ***')
            return False
            
        current_target_node_mec = mec.MecController.get_mec(mec_set, current_target_node)
        extracted_service = mec.MecController.remove_service(current_target_node_mec, service)
        
        mec.MecController.deploy_service(mec_candidate, extracted_service)
        #print("*** Performing migration ***")
        #print(f'service {service.id} moved from MEC {current_target_node_mec.name} to {mec_candidate.name}')
        self.successful_migrations +=1
        return True
        

    
    #TODO: THIS METHOD SHOULD ALSO BE IMPLEMENTED INTO MEC_CONTROLLER.DISCOVER_MEC METHOD!
    #TODO: For this method, we have to implement some sort of penality to count when the service is deployed in a mec that has lower latency than its current mec server however it is higher than 5ms.
    
    def discover_mec(
        self, base_station_set: List['BaseStation'], mec_set: List['Mec'], graph: 'Graph', start_node: 'BaseStation', service: 'VrService'
    ) -> 'Mec':
        #print(f'*** Discovering MEC ***')
    
        shortest_path = dijkstra.DijkstraController.get_shortest_path(
            mec_set, graph, start_node
        )
        # Iterate over the sorted shortest path (list of tuples) and checks whether a mec server can host the service
        for node in shortest_path:    
            bs_name = node[0]
            base_station = bs.BaseStationController.get_base_station_by_name(base_station_set, bs_name)
            bs_mec = mec.MecController.get_mec(mec_set, base_station)
            
            if mec.MecController.check_deployment(bs_mec, service):
                return bs_mec
            
            #print(f'\nMEC {bs_mec.name} is overloaded! Discarting...')
        return None
        
        
    #TODO: we have to implement the restriction of 5ms before migrating a service.admin 
    def trade_off(
        self, base_station_set: List['BaseStation'], mec_set: List['Mec'], vr_users: List['VrHMD'], graph: 'Graph', service: 'VrService'
    ) -> bool:
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""
        #print(f'\n___________________________________________________\n')
        #print(f'\n*** checking service {service.id} ***\n')
        
        service_owner = vr.VrController.get_vr_service_owner(vr_users, service)
        
        """ initializing start and target nodes """
        start_node = bs.BaseStationController.get_base_station(base_station_set, service_owner.current_location)
        #print(f'user is connected in {start_node.name}\n')
        
        mec_candidate = self.discover_mec(base_station_set, mec_set, graph, start_node, service)
        candidate_target_node = mec.MecController.get_mec_bs_location(base_station_set, mec_candidate)
        computing_latency, network_latency, candidate_service_latency = scg.ScgController.get_E2E_latency(
            mec_set, graph, start_node, candidate_target_node
        )
        
        hmd_latency = vr.VrController.get_hmd_latency(base_station_set, vr_users, service_owner.ip)
        
        
        if any(service.id == user_service.id for user_service in service_owner.services_set):
            """ checks whether a service IS deployed on the HMD """
            
            if mec_candidate is not None and candidate_service_latency < hmd_latency:
                return self.offload_service(mec_candidate, vr_users, service_owner, service)

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
            
            current_target_node = mec.MecController.get_service_bs(
                base_station_set, mec_set, service.id
            )
            computing_latency, network_latency, current_service_latency = scg.ScgController.get_E2E_latency(
                mec_set, graph, start_node, current_target_node
            )
            
            #print(f'service is deployed on MEC {current_target_node.name}')
            #print(f'Latencies: hmd: {hmd_latency} | current: {current_service_latency} | candidate: {candidate_service_latency}\n')
            
            if mec_candidate is None:
                candidate_service_latency = sys.maxsize
                
            if current_service_latency > hmd_latency or current_service_latency > candidate_service_latency:
                if hmd_latency < candidate_service_latency:
                    return self.reverse_offloading(mec_set, vr_users, service_owner, service)
                return self.perform_migration(mec_set, mec_candidate, current_target_node, service)

            
            
            # TODO: FIND OUT A WAY TO IMPLEMENT ALPHA IN A PROPPER MANNER HERE.
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
        
                 
        
    

    
    '''
    #TODO: No need to find in all nodes, but just until we find out a node with E2E latency <= 5ms
    def ddiscover_mec(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], graph: Graph, user: VrHMD, service: VrService
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            """ tests if the mec attached to the base station can deploy the service"""
            if ( 
                MecController.check_deployment(
                    mec_set, base_station.mec_id, service
                )
            ):
                #src_bs = BaseStationController.get_base_station(
                #    base_station_set, user.current_location
                #)
                #src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
                aux_path, new_latency = DijkstraController.get_shortest_path(
                    start_node=user.current_location,
                    #start_node_computing_delay=src_mec.computing_latency,
                    #start_node_wireless_delay=src_bs.wireless_latency,
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
    '''