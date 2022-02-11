from migration import Migration
from vr_controller import VrController
from mec.mec import MecAgent

class WorkloadController:

    @staticmethod
    def check_workloads(
        base_station_set: list, 
        mec_set: list, 
        vr_users: list, 
        hosts: list,
        migration: Migration,
    ):
        WorkloadController.check_vr_service_workload(vr_users)
        WorkloadController.check_mec_service_workload(
            base_station_set=base_station_set,
            mec_set=mec_set, 
            vr_users=vr_users,
            hosts=hosts,
            migration=migration,
        )

    @staticmethod
    def check_vr_service_workload(vr_users: list):
        for user in vr_users:
            for service in user.services_set:
                if service.iterations_count >= service.iterations:
                    VrController.change_quota(service)
                    service.iterations_count = 0
                else:
                    service.iterations_count +=1

    @staticmethod
    def check_mec_service_workload(
        base_station_set: list,
        mec_set: list, 
        vr_users: list,
        hosts: list,
        migration: Migration,
    ):
        for mec in mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    if (
                        service.iterations_count >= service.iterations
                    ):
                        extracted_service = MecAgent.remove_service(
                            mec_set, mec.id, service.id
                        )
                        VrController.change_quota(extracted_service)
                        if MecAgent.check_deployment(
                            mec_set=mec_set, mec_id=mec.id, service=extracted_service
                        ):

                            """ checks whether the service fits in the mec """
                            extracted_service.iterations_count = 0
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
                            # FROM NOW ON WE SHOULD CALL AN AGNOSTIC MIGRATION METHOD!
                            migration.service_migration( 
                                base_station_set=base_station_set,
                                mec_set=mec_set,
                                vr_users=vr_users,
                                hosts=hosts,
                                service=service,
                            )
                        
                    else:
                        service.iterations_count += 1
                        