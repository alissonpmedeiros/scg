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
from controllers import vr_controller as vr
from controllers import mec_controller as mec

"""other modules"""
import requests, socket
from typing import List
from munch import DefaultMunch
from requests.exceptions import HTTPError
from pprint import pprint as pprint

class WorkloadController:
    @staticmethod
    def check_migration_demand(
        base_station_set: List['BaseStation'], 
        mec_set: List['Mec'], 
        vr_users: List['VrHMD'], 
        graph: 'Graph', 
        service: 'VrService', 
        extracted_service: 'VrService', 
        service_mec_server: 'Mec', 
        quota_copy: dict, 
        migration: 'Migration',
    ) -> None:
        """
        Checks whether a service fits on a mec server, otherwise, it checks the migration. 
        If migration is not possible, it will revert the service to the previous service quota.  
        """
        
        if mec.MecController.check_deployment(
            service_mec_server, extracted_service
        ):
            mec.MecController.deploy_service(service_mec_server, extracted_service)
        
        else:
            mec.MecController.deploy_service(service_mec_server, extracted_service) 
           
            if not migration.service_migration( 
                base_station_set, mec_set, vr_users, graph, extracted_service
            ):
                extracted_service = mec.MecController.remove_service(
                    service_mec_server, service
                )
                extracted_service.quota = quota_copy
                mec.MecController.deploy_service(service_mec_server, extracted_service)

    @staticmethod
    def update_workloads(
        base_station_set: List['BaseStation'], 
        mec_set: List['Mec'], 
        vr_users: List['VrHMD'],
        graph: 'Graph',
        migration: 'Migration',
    ) -> None:
        """updates vr and mec service workloads"""
        #print('\n################### STARTING WORKLOAD CHECK #######################')   
        response_vr_users = WorkloadController.get_workloads()
        for response_user in response_vr_users:
            for response_service in response_user.services_set:
                service_mec_server = mec.MecController.get_service_mec_server(
                    mec_set, response_service.id
                )
                service = None
                if not service_mec_server:
                    service_owner = vr.VrController.get_vr_service_owner(
                        vr_users, response_service
                    )
                    service = vr.VrController.get_vr_service(
                        vr_users, service_owner.ip, response_service.id
                    )
                    service.quota = response_service.quota
                   
                else:
                    service = mec.MecController.get_mec_service(mec_set, response_service.id)
        
                    extracted_service = mec.MecController.remove_service(
                        service_mec_server, service
                    )
                    
                    quota_copy = extracted_service.quota
                    extracted_service.quota  = response_service.quota
                    WorkloadController.check_migration_demand(
                        base_station_set, 
                        mec_set, 
                        vr_users, 
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
        """gets the new workloads from the web servers"""
        HOST_IP=socket.gethostbyname(socket.gethostname())
        URL = "http://{}:5000/".format(HOST_IP)
        try: 
            response = requests.get(URL)
            if response.status_code == 200:
                data = response.json()['users']
                result = DefaultMunch.fromDict(data)
                #print('*** GOT WORKLOADS ***')
                return result
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

    