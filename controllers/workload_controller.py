import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph
    from models.vr import VrService
    from models.migration_ABC import Migration
    from models.base_station import BaseStation

""" controller modules """
from controllers import vr_controller 
from controllers import mec_controller 
from controllers import json_controller

"""other modules"""
import requests, socket
from typing import Dict
from requests.exceptions import HTTPError


class WorkloadController:
    @staticmethod
    def check_migration_demand(
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService', 
        extracted_service: 'VrService', 
        service_mec_server: 'Mec', 
        quota_copy: str, 
        migration: 'Migration',
    ) -> None:
        """
        Checks whether a service fits on a mec server, otherwise, it checks the migration. 
        If migration is not possible, it will revert the service to the previous service quota.  
        """
        
        if mec_controller.MecController.check_deployment(
            service_mec_server, extracted_service
        ):
            mec_controller.MecController.deploy_service(
                service_mec_server, extracted_service
            )
        
        else:
            mec_controller.MecController.deploy_service(
                service_mec_server, extracted_service
            ) 
           
            if not migration.service_migration( 
                base_station_set, mec_set, hmds_set, graph, extracted_service
            ):
                extracted_service = mec_controller.MecController.remove_service(
                    service_mec_server, service
                )
                extracted_service.quota.set_quota(quota_copy)
                mec_controller.MecController.deploy_service(
                    service_mec_server, extracted_service
                )

    @staticmethod
    def update_workloads(
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'],
        graph: 'Graph',
        migration: 'Migration',
    ) -> None:
        """updates vr and mec service workloads"""
        #print('\n################### STARTING WORKLOAD CHECK #######################')   
        response_hmds_set: Dict[str, 'VrHMD'] = WorkloadController.get_workloads()
        
        for response_id, response_hmd in response_hmds_set.items():
            for response_service in response_hmd.services_set:
                service_mec_server_id, service_mec_server = mec_controller.MecController.get_service_mec_server(
                    mec_set, response_service.id
                )
                service: 'VrService' = None
                if not service_mec_server:
                    service_owner_id, service_owner = vr_controller.VrController.get_vr_service_owner(
                        hmds_set, response_service
                    )
                    
                    service = vr_controller.VrController.get_vr_service(
                        hmds_set, service_owner_id, response_service.id
                    )
                    
                else:
                    service = mec_controller.MecController.get_mec_service(
                        mec_set, response_service.id
                    )
        
                    extracted_service = mec_controller.MecController.remove_service(
                        service_mec_server, service
                    )
                    
                    quota_copy = extracted_service.quota.name
                    extracted_service.quota.set_quota(response_service.quota.name)
                    
                    WorkloadController.check_migration_demand(
                        base_station_set, 
                        mec_set, 
                        hmds_set, 
                        graph,
                        service, 
                        extracted_service, 
                        service_mec_server, 
                        quota_copy, 
                        migration
                    )
                    
        #print('\n################### FINISH WORKLOAD CHECK #######################\n')    
        return  
                                                         
    @staticmethod
    def get_workloads() -> dict:
        """gets the new workloads from the web server"""
        
        HOST_IP=socket.gethostbyname(socket.gethostname())
        URL = "http://{}:5000/".format(HOST_IP)
        try: 
            response = requests.get(URL)
            if response.status_code == 200:
                data = response.json()
                transcoded_data = json_controller.DecoderController.loading_to_dict(data)
                return transcoded_data
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

    