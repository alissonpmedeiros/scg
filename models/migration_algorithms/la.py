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


class LA(Migration):
    """provides a network latency aware (LA) service migration algorithm that considers the resources of the MECs before performing migrations"""
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph'
    ) -> None:
        return super().check_services(
            base_station_set, mec_set, hmds_set, graph
        )

    def service_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        return self.perform_migration(
            base_station_set, mec_set, hmds_set, graph, service
        )

    def perform_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between hmd_ip and where the service is deployed
        """
        
        service_owner_id, service_owner = vr_controller.VrController.get_vr_service_owner(
            hmds_set, service
        )
        
        start_node = bs_controller.BaseStationController.get_base_station(
            base_station_set, service_owner.current_location
        )
        
        mec_candidate_id, mec_candidate = self.discover_mec(
            base_station_set, mec_set, graph, start_node, service
        )
        
        if mec_candidate is not None:
            
            """getting the current service latency"""
            start_node = bs_controller.BaseStationController.get_base_station(
                base_station_set, service_owner.current_location
            )    
            
            current_target_node = mec_controller.MecController.get_service_bs(
                base_station_set, mec_set, service.id
            )
            
            current_latency = scg_controller.ScgController.get_E2E_latency(
                mec_set, graph, start_node, current_target_node
            )
            
            current_service_latency = current_latency.get('e2e_latency')
            
            
            """getting the candidate latency"""
            candidate_target_node = mec_controller.MecController.get_mec_bs_location(
                base_station_set, mec_candidate_id
            )
        
        
            candidate_latency = scg_controller.ScgController.get_E2E_latency(
                mec_set, graph, start_node, candidate_target_node
            )

            candidate_service_latency = candidate_latency.get('e2e_latency')
            
            
            if current_service_latency > candidate_service_latency:
                service_mec_server_id, service_mec_server = mec_controller.MecController.get_service_mec_server(
                    mec_set, service.id
                )
                
                extracted_service = mec_controller.MecController.remove_service(
                    service_mec_server, service
                )
                
                mec_controller.MecController.deploy_service(
                    mec_candidate, extracted_service
                )
                self.successful_migrations += 1
                return True
            
            self.unsuccessful_migrations += 1
            return False
        else:
            self.unsuccessful_migrations += 1
            return False

            
    def discover_mec( 
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        graph: 'Graph', 
        start_node: 'BaseStation', 
        service: 'VrService'
    ) -> 'Mec':
        """ discovers a nearby MEC server to either offload or migrate the service"""
        
        shortest_path = dijkstra_controller.DijkstraController.get_shortest_path(
            mec_set, graph, start_node
        )
        
        """
        Iterate over the sorted shortest path (list of tuples) and checks only the best mec 
        server can host the service without considering the resource availability of other candidates
        """
        
        for node in shortest_path:    
            bs_name = node[0]
            bs_id, base_station = bs_controller.BaseStationController.get_base_station_by_name(
                base_station_set, bs_name
            )
            
            bs_mec = mec_controller.MecController.get_mec(mec_set, base_station)
            
            if mec_controller.MecController.check_deployment(bs_mec, service):
                return base_station.mec_id, bs_mec
            
            #print(f'\nMEC {bs_mec.name} is overloaded! cancelling the process...')
            return None, None
        
