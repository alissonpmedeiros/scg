import requests, socket
from mec.mec import MecAgent
from munch import DefaultMunch
from requests.exceptions import HTTPError
from vr.vr import VrService
from vr.vr_controller import VrController
from migration.migration_ABC import Migration

class WorkloadController:
    
    @staticmethod
    def check_migration_demand(
        base_station_set: list, 
        mec_set: list, 
        vr_users: list, 
        service: VrService, 
        extracted_service: VrService, 
        service_server_id: str, 
        quota_copy: dict, 
        migration: Migration 
    ) -> None:
        """_summary_

        Checks whether a service fits on a mec server, otherwise, this method  chekcs the migration. 
        If migration is not possible, it will revert the service to the previous service quota.  

        Arguments:
            base_station_set -- _description_
            mec_set -- _description_
            vr_users -- _description_
            service -- _description_
            service_server_id -- _description_
            quota_copy -- _description_
            migration -- _description_
        """
        if MecAgent.check_deployment(
            mec_set=mec_set, mec_id=service_server_id, service=extracted_service
        ):
            MecAgent.deploy_service(mec_set, service_server_id, extracted_service)
        
        else:
            MecAgent.deploy_service(mec_set, service_server_id, extracted_service)
            
            if not migration.service_migration( 
                base_station_set=base_station_set,
                mec_set=mec_set,
                vr_users=vr_users,
                service=extracted_service,
            ):
                extracted_service = MecAgent.remove_service(
                    mec_set, service_server_id, service.id
                )
                extracted_service.quota = quota_copy
                MecAgent.deploy_service(mec_set, service_server_id, extracted_service)

    @staticmethod
    def update_workloads(
        base_station_set: list, 
        mec_set: list, 
        vr_users: list,
        migration: Migration,
    ):
        """updates vr and mec service workloads"""
        response_vr_users = WorkloadController.get_workloads()
        
        for response_user in response_vr_users:
            for response_service in response_user.services_set:
                service_server_id = MecAgent.get_service_server_id(mec_set, response_service.id)
                service = None
                if not service_server_id:
                    service_owner = VrController.get_vr_service_owner(
                        vr_users=vr_users, service=response_service
                    )
                    service = VrController.get_vr_service(
                        vr_users, service_owner.ip, response_service.id
                    )
                    service.quota = response_service.quota
                else:
                    service = MecAgent.get_mec_service(mec_set, response_service.id)
                    
                    extracted_service = MecAgent.remove_service(
                        mec_set, service_server_id, service.id
                    )
                    quota_copy = extracted_service.quota
                    extracted_service.quota  = response_service.quota
                    WorkloadController.check_migration_demand(
                        base_station_set, mec_set, vr_users, service, extracted_service, service_server_id, quota_copy, migration
                    )
                    
                        
                                                         
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
                print('\n\n*** GOT WORKLOADS ***')
                return result
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

    