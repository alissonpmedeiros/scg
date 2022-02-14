import time
from vr import VrService
from mec.mec import MecAgent
from scg import ScgController
from vr_controller import VrController
from migration.migration import Migration
from mec.mec_controller import MecController
from base_station import BaseStationController

class AlwaysMigrate(Migration):
    """ implements the migration behaviour trigered by handover """


    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, base_station_set: list, mec_set: list, vr_users: list, hosts: list
    ):
        return super().check_services(base_station_set, mec_set, vr_users, hosts)
    
    
    def service_migration(
        self, 
        base_station_set: list, 
        mec_set: list, 
        vr_users: list, 
        hosts: list, 
        service: VrService,
    ):
        
        service_owner = VrController.get_vr_service_owner(
            vr_users=vr_users, service=service
        )
        
        AlwaysMigrate.perform_migration(
            base_station_set=base_station_set,
            mec_set=mec_set,
            hosts=hosts,
            user=service_owner,
            service=service,
        )
        time.sleep(1)


    @classmethod
    def perform_migration(
        self,
        base_station_set: list,
        mec_set: list,
        hosts: list, 
        user: dict,
        service: VrService,
    ):
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """

        user_bs_location = VrController.get_vr_user_location(hosts=hosts, user_ip=user.ip)

        service_bs_location = MecAgent.get_service_bs_location(
            base_station_set, mec_set, service.id
        )
        
        if user_bs_location != service_bs_location:
            service_server_id = MecAgent.get_service_server_id(mec_set, service.id)
            user_bs = BaseStationController.get_base_station(
                base_station_set=base_station_set, bs_id=user_bs_location
            )


            if MecAgent.check_deployment(
                mec_set=mec_set, mec_id=user_bs.mec_id, service=service
            ):

                extracted_service = MecAgent.remove_service(
                    mec_set, service_server_id, service.id
                )
                MecAgent.deploy_service(mec_set, user_bs.mec_id, extracted_service)
                #print("*** Performing migration ***")
                # print("service {} moved from MEC {} to {}".format(service.id, service_server_id, mec_id_candidate))
                # print("new latency: {}\n".format(new_service_latency))
                self.sucessful_migrations += 1

            else:
                #print("\n*** Migration failed. Error: no candidates ***")
                self.unsuccessful_migrations += 1




    