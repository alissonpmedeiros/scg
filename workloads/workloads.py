import requests
from mec.mec import MecAgent
from vr_controller import VrController
from requests.exceptions import HTTPError
from migration.migration import Migration
from munch import DefaultMunch

class WorkloadController:

    @staticmethod
    def update_workloads(
        base_station_set: list, 
        mec_set: list, 
        vr_users: list,
        migration: Migration,
    ):
        """updates vr and mec service workloads"""
        response_vr_users = WorkloadController.get_workloads()
        WorkloadController.update_vr_service_workloads(vr_users, response_vr_users)
        WorkloadController.update_mec_service_workloads(
            base_station_set=base_station_set,
            mec_set=mec_set, 
            vr_users=vr_users,
            migration=migration,
            response_vr_users=response_vr_users,
        )

    @staticmethod
    def update_vr_service_workloads(
        vr_users: list,
        response_vr_users: list,
    ) -> None:
        """updates vr service workloads"""
        for user in vr_users:
            for service in user.services_set:
                response_service = VrController.get_service(response_vr_users, service.id)
                service.quota = response_service.quota
                

    @staticmethod
    def update_mec_service_workloads(
        base_station_set: list,
        mec_set: list, 
        vr_users: list,
        migration: Migration,
        response_vr_users: list,
    ) -> None:
        """updates mec service workloads"""
        for mec in mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    response_service = VrController.get_service(response_vr_users, service.id)
                    extracted_service = MecAgent.remove_service(
                        mec_set, mec.id, service.id
                    )
                    extracted_service.quota = response_service.quota
                    if MecAgent.check_deployment(
                        mec_set=mec_set, mec_id=mec.id, service=extracted_service
                    ):

                        """ checks whether the service fits in the mec """
                        MecAgent.deploy_service(
                            mec_set=mec_set,
                            mec_id=mec.id,
                            service=extracted_service,
                        )
                    else:
                        """ otherwise, the service should be migrated! """ 
                        MecAgent.deploy_service(
                            mec_set=mec_set,
                            mec_id=mec.id,
                            service=extracted_service,
                        )
                        migration.service_migration( 
                            base_station_set=base_station_set,
                            mec_set=mec_set,
                            vr_users=vr_users,
                            service=service,
                        )
                                                         
    @staticmethod
    def get_workloads() -> dict:
        """gets the new workloads from the web servers"""
        URL = "http://127.0.0.1:5000/"
        try: 
            response = requests.get(URL)
            if response.status_code == 200:
                data = DefaultMunch.fromDict(response.json()['users'])
                return data
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')