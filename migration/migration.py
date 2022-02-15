from mec.mec_controller import MecController
from vr import VrService
from vr_controller import VrController
from dataclasses import dataclass
from scg import ScgController
from mec.mec import MecAgent
from react import REACTApproach
import time

from abc import ABC, abstractmethod




"""abstract base classes let you define a class with abstract methods, which all subclasses must implement in order to be initialized"""
class Migration(ABC):
    sucessful_migrations = 0
    unsuccessful_migrations = 0

    def get_migrations(self):
        print("SUCESSFUL MIGRATIONS: {}".format(self.sucessful_migrations))
        print("UNSUCCESFUL MIGRATIONS: {}".format(self.unsuccessful_migrations))

    def check_services(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
    ):
        for user in vr_users:
            if user.current_location != user.previous_location:
                print('UPDATING USER {} LOCATION: NEW {} | PREVIOUS: {}'.format(user.ip, user.current_location, user.previous_location))
                for service_id in user.services_ids:
                    service = None
                    if any(service_id == service.id for service in user.services_set): 
                        service=user.services_set[0]
                    else: 
                        service = MecAgent.get_service(mec_set, service_id)
                    self.service_migration(
                        base_station_set=base_station_set,
                        mec_set=mec_set,
                        vr_users=vr_users,
                        service=service,
                    )
        time.sleep(0.5)
        


    def service_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        service: VrService
    ):
        pass    


class SCG(Migration):
    """ implements SCG algorithm """

    def check_services(self, base_station_set: list, mec_set: list, vr_users: list):
        return super().check_services(base_station_set, mec_set, vr_users)

    def get_migrations(self):
        return super().get_migrations()
        

    def service_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list, 
        service: VrService,
    ):
        SCG.trade_off(
            base_station_set=base_station_set,
            mec_set=mec_set,
            vr_users=vr_users,
            service=service,
        )
        

    @classmethod
    def reverse_offloading(
        self, 
        mec_set: list, 
        vr_users: list, 
        user_ip: str, 
        service_id: str
    ) -> None:
        """ offloads a service i back to vr hmd """

        service_server_id = MecAgent.get_service_server_id(mec_set, service_id)
        extracted_service = MecAgent.remove_service(
            mec_set, service_server_id, service_id
        )

        VrController.deploy_vr_service(
            vr_users=vr_users, user_ip=user_ip, service=extracted_service
        )

    """ ADJUST THIS METHOD TO USE ONLY CALCULATE NET LATENCY INSTEAD OF ETE LATENCY. THEN, THIS METHOD SHOULD BE USED WIHTIN CLASS 'NetLatencyMigration' """
    @classmethod
    def perform_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        user_ip: str,
        service_id: str, 
    ):
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """
        user = VrController.get_vr_user(vr_users=vr_users, user_ip=user_ip)

        service_content = MecAgent.get_service(mec_set, service_id)
        service_server_id = MecAgent.get_service_server_id(mec_set, service_id)
        service_location = MecAgent.get_service_bs_location(
            base_station_set, mec_set, service_id
        )
        previous_service_latency = ScgController.get_ETE_latency(
            base_station_set=base_station_set,
            mec_set=mec_set,
            src_location=user.current_location,
            dst_location=service_location,
        )

        mec_id_candidate = MecController.discover_mec(
            base_station_set=base_station_set,
            mec_set=mec_set,
            user=user,
            service=service_content,
        )

        mec_candidate_location = MecAgent.get_mec_bs_location(
            base_station_set, mec_id_candidate
        )

        if mec_candidate_location is not None:
            new_service_latency = ScgController.get_ETE_latency(
                base_station_set=base_station_set,
                mec_set=mec_set,
                src_location=user.current_location,
                dst_location=mec_candidate_location,
            )

            if new_service_latency < previous_service_latency:
                extracted_service = MecAgent.remove_service(
                    mec_set, service_server_id, service_id
                )
                MecAgent.deploy_service(mec_set, mec_id_candidate, extracted_service)
                #print("*** Performing migration ***")
                # print("service {} move from MEC {} to {}".format(service_id, service_server_id, mec_id_candidate))
                # print("new latency: {}\n".format(new_service_latency))
                self.sucessful_migrations += 1

        else:
            print("*** Migration failed. Error: no candidates ***")
            self.unsuccessful_migrations += 1

    @classmethod
    def trade_off(
        self, 
        base_station_set: list, 
        mec_set: list, 
        vr_users: list,
        service: VrService,
    ):
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

            vr_service_content = VrController.get_vr_service(
                vr_users=vr_users, 
                user_ip=service_owner.ip, 
                service_id=service.id,
            )

            mec_id_candidate = MecController.discover_mec(
                base_station_set=base_station_set,
                mec_set=mec_set,
                user=service_owner,
                service=vr_service_content,
            )

            mec_candidate_location = MecAgent.get_mec_bs_location(
                base_station_set, mec_id_candidate
            )

            if mec_candidate_location is not None:
                new_service_latency = ScgController.get_ETE_latency(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    src_location=service_owner.current_location,
                    dst_location=mec_candidate_location,
                )

                if new_service_latency < hmd_latency:
                    extracted_service = VrController.remove_vr_service(
                        vr_users=vr_users,
                        user_ip=service_owner.ip,
                        service_id=service.id,
                    )

                    MecAgent.deploy_service(
                        mec_set, mec_id_candidate, extracted_service
                    )
                    #print("*** Performing offloading ***")
                    # print("service {} move from HMD {} to MEC {}".format(service_id, user.ip, mec_id_candidate))
                    # print("hmd latency: {}".format(hmd_latency))
                    # print("new latency: {}\n".format(new_service_latency))
                    # a = input("")

            else:
                print("**** no candidates ****")
                """
                Migration should be considered. However, there are no mec servers available. 
                The service stays on the HMD. 
                We should consider a service migration violation... 
                """

        else:
            """ otherwise, the service is deployed on MEC servers"""
            service_location = MecAgent.get_service_bs_location(
                base_station_set, mec_set, service.id
            )

            """ 
            measures the latency between bs where the user 
            is connected and the mec where the service is deployed 
            """
            '''
            '''
            if service_location is None or service_owner.current_location is None:
                print("\nservice ID: {}".format(service.id))
                print("\nservice location: {}".format(service_location))
                print("\nservice owner: {}".format(service_owner))
                print("\nservice owner location: {}".format(service_owner.current_location))
                print(
                    "GOT AN ERROR: SERVICE LOCATION OR USER LOCATION NOT FOUND!"
                )
                a = input("")

            current_service_latency = ScgController.get_ETE_latency(
                base_station_set=base_station_set,
                mec_set=mec_set,
                src_location=service_owner.current_location,
                dst_location=service_location,
            )

            hmd_latency = VrController.get_hmd_latency(
                base_station_set=base_station_set,
                vr_users=vr_users,
                user_ip=service_owner.ip,
            )

            # print('\n')
            # print('service id: {}'.format(service_id))
            # print('service location: {}'.format(service_location))
            # print('service latency: {}'.format(current_service_latency))
            # print('hmd {} has latency: {}'.format(user.ip, hmd_latency))

            if current_service_latency <= hmd_latency:
                # print('service remains on mec servers. \nstarting migration check')
                SCG.perform_migration(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    vr_users=vr_users,
                    user_ip=service_owner.ip,
                    service_id=service.id,
                )
            else:
                #print("*** Performing reverse offloading ***")
                SCG.reverse_offloading(
                    mec_set=mec_set,
                    vr_users=vr_users,
                    user_ip=service_owner.ip,
                    service_id=service.id,
                )

'''
class REACT(Migration):
    
    @staticmethod
    def service_migration(
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        migration: MigrationController,
        service: VrService,
    ):
        REACTApproach.solidarity(
            mec_set=mec_set, 
            current_mec_id='TBD', ### TO BE DEFINED! 
            service=service,
        )

# TO ANALYZE THE IMPACT OF REACT, WE HAVE TO ADAPT THE SYSTEM DO CATCH A SITUATION WHERE THE BEST SERVER IS ALWAYS CONSIDER, REGARDLESS THE RESOURCE AVAILABILITY            



class NoMigration(Migration):
    """ implements the no migration behaviour """

    def service_migration(base_station_set: list, mec_set: list, vr_users: list):
        pass


class NetLatencyMigration(Migration):
    """ implements the migration behaviour based on net latency """

    def service_migration(base_station_set: list, mec_set: list, vr_users: list):
        pass


class AUB(Migration):
    """ implements the algorithm Average Utilization Based (AUB) Migration """

    def service_migration(base_station_set: list, mec_set: list, vr_users: list):
        pass

        """ 
        Describe the algorithm: 
        (i) SFCs should be placed on the paths where link latency is as optimal as possible; 
        (ii) processing capacity of VNFs can be improved to reduce response latency by allocating more resources to those VNFs. AUB only considers (ii), while SCG consider both. 
        
        1. Both under-utilized and over-utilized servers are first identified
        2. For each over-utilized server, one or more VNFs are selected as victim VNFs based on Eq. (20
        3. Afterwards, optimal servers are chosen from under-utilized servers for these victim VNFs using policy of choosing target server
        4.
        """

'''