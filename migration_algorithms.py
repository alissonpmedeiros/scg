
from base_station import BaseStationController
from mec.mec import MecController, MecAgent
from architecture import ScgController
from vr_controller import VrController
from dataclasses import dataclass

import time

@dataclass
class SCG:
    """ implements SCG algorithm """

    @staticmethod
    def reverse_offloading( 
        mec_set: list, 
        vr_users:list, 
        user_ip: str, 
        service_id: str) -> None:
        """ offloads a service i back to vr hmd """ 
        
        service_server_id = MecAgent.get_service_server_id(
            mec_set, 
            service_id)
        extracted_service = MecAgent.remove_service(
            mec_set,  
            service_server_id, 
            service_id)

        VrController.deploy_vr_service( 
            vr_users=vr_users, 
            user_ip=user_ip, 
            service=extracted_service)

    @staticmethod
    def migration(  
        base_station_set: list, 
        mec_set:list, 
        vr_users: list, 
        user_ip: str, 
        service_id: str):
        """ provides the service migration of service i, which is bases on the current distance between user_ip and where the service is deployed """
        
        user_location = VrController.get_vr_user_location(user_ip=user_ip)
        
        service_content = MecAgent.get_service(mec_set, service_id)
        service_server_id = MecAgent.get_service_server_id(mec_set, service_id)
        service_location = MecAgent.get_service_bs_location(
            base_station_set, 
            mec_set, 
            service_id)
        previous_service_latency = ScgController.calculate_ETE(
            base_station_set=base_station_set, 
            mec_set=mec_set, 
            src_location=user_location, 
            dst_location=service_location)

        mec_id_candidate = MecController.discover_mec(
            base_station_set=base_station_set, 
            mec_set=mec_set, 
            vr_ip=user_ip, 
            service=service_content)

        mec_candidate_location = MecAgent.get_mec_bs_location(
            base_station_set,
            mec_id_candidate)
        
        if mec_candidate_location is not None:
            new_service_latency = ScgController.calculate_ETE(
                base_station_set=base_station_set, 
                mec_set=mec_set, 
                src_location=user_location, 
                dst_location=mec_candidate_location)

            if new_service_latency < previous_service_latency:
                extracted_service = MecAgent.remove_service(
                    mec_set,  
                    service_server_id, 
                    service_id)
                MecAgent.deploy_service(
                    mec_set, 
                    mec_id_candidate, 
                    extracted_service)
                print("\n*** Performing migration ***")
                print("service {} move from MEC {} to {}".format(
                    service_id, 
                    service_server_id, 
                    mec_id_candidate))
                print("new latency: {}\n".format(new_service_latency))
                
        else:
            print("**** no candidates ****")
            """ 
            Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation...
            
            ACCEPTANCE RATION COMES HERE...
            
            """ 

    @staticmethod
    def trade_off(
        base_station_set: list, 
        mec_set:list, 
        vr_users: list ):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""

        for user in vr_users:
            for service_id in user.services_ids:
                user_location = VrController.get_vr_user_location(user_ip=user.ip)
                if any (service['id'] == service_id for service in user.services_set):    
                    """ checks whether a service IS deployed on the HMD, then we need to check the feasability of offloading this particular service to mec servers """

                    hmd_latency = VrController.get_hmd_latency(
                        base_station_set=base_station_set, 
                        vr_users=vr_users, 
                        user_ip=user.ip)

                    vr_service_content = VrController.get_vr_service(
                        vr_users=vr_users, 
                        user_ip=user.ip, 
                        service_id=service_id)

                    mec_id_candidate = MecController.discover_mec(
                        base_station_set=base_station_set, 
                        mec_set=mec_set, 
                        vr_ip=user.ip, 
                        service=vr_service_content)

                    mec_candidate_location = MecAgent.get_mec_bs_location(
                        base_station_set, 
                        mec_id_candidate)
                    
                    if mec_candidate_location is not None:
                        new_service_latency = ScgController.calculate_ETE(
                            base_station_set=base_station_set, 
                            mec_set=mec_set, 
                            src_location=user_location, 
                            dst_location=mec_candidate_location)

                        if new_service_latency < hmd_latency:
                            extracted_service = VrController.remove_vr_service(
                                vr_users=vr_users, 
                                user_ip=user.ip, 
                                service_id=service_id)
                            
                            MecAgent.deploy_service(
                                mec_set, 
                                mec_id_candidate, 
                                extracted_service)
                            print("\n*** Performing migration ***")
                            print("service {} move from HMD {} to MEC {}".format(
                                service_id, 
                                user.ip, 
                                mec_id_candidate))
                            print("hmd latency: {}".format(hmd_latency))
                            print("new latency: {}\n".format(new_service_latency))
                            #a = input("")
                            
                    else:
                        print("**** no candidates ****")
                        """ Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation... """
                    
                else:
                    """ otherwise, the service is deployed on MEC servers"""
                    service_location = MecAgent.get_service_bs_location(
                        base_station_set, 
                        mec_set, 
                        service_id)
                    
                    """ measures the latency between bs where the user is connected and the mec where the service is deployed """
                    if service_location is None or user_location is None:
                        print("service location: {}".format(service_location))
                        print("user location: {}".format(user_location))
                        a = input("")
            
                    current_service_latency = ScgController.calculate_ETE(
                        base_station_set=base_station_set, 
                        mec_set=mec_set, 
                        src_location=user_location, 
                        dst_location=service_location)

                    hmd_latency = VrController.get_hmd_latency(
                        base_station_set=base_station_set, 
                        vr_users=vr_users, 
                        user_ip=user.ip)

                    print('\n')
                    print('service id: {}'.format(service_id))
                    print('service location: {}'.format(service_location))
                    print('service latency: {}'.format(current_service_latency))
                    print('hmd {} has latency: {}'.format(user.ip, hmd_latency))

                    if current_service_latency <= hmd_latency:
                        print('service remains on mec servers. \nstarting migration check')
                        SCG.migration(
                            base_station_set=base_station_set, 
                            mec_set=mec_set, 
                            vr_users=vr_users, 
                            user_ip=user.ip, 
                            service_id=service_id)
                    else:
                        print('service should be reverse offloaded to hmd')
                        SCG.reverse_offloading(mec_set=mec_set, 
                        vr_users=vr_users, 
                        user_ip=user.ip, 
                        service_id=service_id)
               

            time.sleep(0.1)


@dataclass
class AlwaysMigrate:
    """ implements the no migration behaviour """
    
    @staticmethod
    def migration(base_station_set: list, mec_set:list, vr_users: list ):
        pass


@dataclass
class NoMigration:
    """ implements the no migration behaviour """
    
    @staticmethod
    def migration(base_station_set: list, mec_set:list, vr_users: list ):
        pass

    

@dataclass
class AUB:
    """ implements the algorithm Average Utilization Based (AUB) Migration """
    
    @staticmethod
    def migration(base_station_set: list, mec_set:list, vr_users: list ):
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


