#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field

""" mec modules """
from mec.mec import MecController, MecResources, MecWorkloads, Mec, MecAgent

""" base station modules """
from base_station import BaseStationController

""" graph modules """
from graph import Dijkstra

""" vr controller modules """
from vr_controller import VrController


""" other modules """
from typing import List
from pprint import pprint as pprint   
import time, json, os


@dataclass
class ScgController:
    """ SCG controller representation """
    services_per_user = 4
    overall_mecs: int = field(default = 100)
    base_station_set: List[dict] = field(default_factory=list, init=False)
    mec_set: List[Mec] = field(default_factory=list, init=False)
    vr_users: List[list] = field(default_factory=list, init=False)


    def __post_init__(self):
        MecController.init_servers(self.overall_mecs)
        self.mec_set = MecController.load_mec_servers()
        
        BaseStationController.build_network_topology(base_station_set=self.base_station_set, mec_set=self.mec_set)
        
        VrController.init_vr_users(vr_users=self.vr_users, services_per_user=self.services_per_user)
        self.vr_users = VrController.load_vr_users()
        
        self.offload_services()
           

    def calculate_ETE(self, src_location: str, dst_location: str) -> float:
        """ calculates the end-to-end latency between two entities """
        
        path, net_latency = Dijkstra.init_algorithm(base_station_set=self.base_station_set, start_node=src_location, target_node=dst_location)

        base_station = BaseStationController.get_base_station(base_station_set=self.base_station_set, bs_id=dst_location)

        mec = MecController.get_mec(mec_set=self.mec_set, mec_id=base_station.mec_id)

        computing_latency = mec.computing_latency 

        ete_latency = net_latency + computing_latency

        #print(" -> ".join(path))
        #print("latency: {}".format(ete_latency))
        return round(ete_latency, 2)

    def service_migration(self, user_ip: str, service_id: str) -> None:
        """ provides the service migration of service i, which is bases on the current distance between user_ip and where the service is deployed """
        user_location = VrController.get_vr_user_location(user_ip=user_ip)
        
        service_content = MecAgent.get_service(self.mec_set, service_id)
        service_server_id = MecAgent.get_service_server_id(self.mec_set, service_id)
        service_location = MecAgent.get_service_bs_location(self.base_station_set, self.mec_set, service_id)
        previous_service_latency = self.calculate_ETE(src_location=user_location, dst_location=service_location)

        mec_id_candidate = MecController.discover_mec(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_ip=user_ip, service=service_content)

        mec_candidate_location = MecAgent.get_mec_bs_location(self.base_station_set, mec_id_candidate)
        
        if mec_candidate_location is not None:
            new_service_latency = self.calculate_ETE(src_location=user_location, dst_location=mec_candidate_location)

            if new_service_latency < previous_service_latency:
                extracted_service = MecAgent.remove_service(self.mec_set,  service_server_id, service_id)
                MecAgent.deploy_service(self.mec_set, mec_id_candidate, extracted_service)
                print("\n*** Performing migration ***")
                print("service {} move from MEC {} to {}".format(service_id, service_server_id, mec_id_candidate))
                print("new latency: {}\n".format(new_service_latency))
                
        else:
            print("**** no candidates ****")
            """ Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation... """

    def offload_service_instance(self) -> None:
        pass            
    
    def offload_services(self) -> None:
        for user in self.vr_users:
            for service_id in user.services_ids:
                extract_service = VrController.remove_vr_service(vr_users=self.vr_users, user_ip=user.ip, service_id=service_id)
                mec_id_dst = MecController.discover_mec(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_ip=user.ip, service=extract_service)

                if mec_id_dst is not None:
                    MecAgent.deploy_service(self.mec_set, mec_id_dst, extract_service)
                else:
                    print("could not deploy the following service: {}".format(extract_service))

                #print('service {} moved from HMD {} to mec {} \n'.format(service_id, user.ip, mec_id_dst))   

    def reverse_offloading(self, user_ip: str, service_id: str) -> None:
        """ offloads a service i back to vr hmd """ 
        
        service_server_id = MecAgent.get_service_server_id(self.mec_set, service_id)
        extracted_service = MecAgent.remove_service(self.mec_set,  service_server_id, service_id)

        VrController.deploy_vr_service(vr_users=self.vr_users, user_ip=user_ip, service=extracted_service)
              
    def get_hmd_latency(self, user_ip: str) -> float:
        """ gets hmd latency, including the wireless latency where the user is connected to """
        user_location = VrController.get_vr_user_location(user_ip=user_ip)
        bs_location = BaseStationController.get_base_station(base_station_set=self.base_station_set, bs_id=user_location)
        user = VrController.get_vr_user(vr_users=self.vr_users, user_ip=user_ip)

        latency = round(bs_location.wireless_latency + user.computing_latency, 2) 

        return latency

    def trade_off(self):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""

        for user in self.vr_users:
            for service_id in user.services_ids:
                user_location = VrController.get_vr_user_location(user_ip=user.ip)
                if any (service['id'] == service_id for service in user.services_set):    
                    """ checks whether a service IS deployed on the HMD, then we need to check the feasability of offloading this particular service to mec servers """

                    hmd_latency = self.get_hmd_latency(user_ip=user.ip)

                    vr_service_content = VrController.get_vr_service(vr_users=self.vr_users, user_ip=user.ip, service_id=service_id)

                    mec_id_candidate = MecController.discover_mec(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_ip=user.ip, service=vr_service_content)

                    mec_candidate_location = MecAgent.get_mec_bs_location(self.base_station_set, mec_id_candidate)
                    
                    if mec_candidate_location is not None:
                        new_service_latency = self.calculate_ETE(src_location=user_location, dst_location=mec_candidate_location)

                        if new_service_latency < hmd_latency:
                            extracted_service = VrController.remove_vr_service(vr_users=self.vr_users, user_ip=user.ip, service_id=service_id)
                            
                            MecAgent.deploy_service(self.mec_set, mec_id_candidate, extracted_service)
                            print("\n*** Performing migration ***")
                            print("service {} move from HMD {} to MEC {}".format(service_id, user.ip, mec_id_candidate))
                            print("hmd latency: {}".format(hmd_latency))
                            print("new latency: {}\n".format(new_service_latency))
                            #a = input("")
                            
                    else:
                        print("**** no candidates ****")
                        """ Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation... """
                    
                else:
                    """ otherwise, the service is deployed on MEC servers"""
                    service_location = MecAgent.get_service_bs_location(self.base_station_set, self.mec_set, service_id)
                    
                    """ measures the latency between bs where the user is connected and the mec where the service is deployed """
                    current_service_latency = self.calculate_ETE(src_location=user_location, dst_location=service_location)

                    hmd_latency = self.get_hmd_latency(user_ip=user.ip)

                    print('\n')
                    print('service id: {}'.format(service_id))
                    print('service location: {}'.format(service_location))
                    print('service latency: {}'.format(current_service_latency))
                    print('hmd {} has latency: {}'.format(user.ip, hmd_latency))

                    if current_service_latency <= hmd_latency:
                        print('service remains on mec servers. \nstarting migration check')
                        self.service_migration(user_ip=user.ip, service_id=service_id)
                    else:
                        print('service should be reverse offloaded to hmd')
                        self.reverse_offloading(user_ip=user.ip, service_id=service_id)
               

            time.sleep(0.1)
        



def start_system() -> None:
    scg = ScgController()
    #MecController.print_mecs(scg.base_station_set, scg.mec_set)
    #a = input("start check migration!")
    '''
    while True:
        print("\n\n##############################\n")
        scg.service_migration()
        time.sleep(1)
    '''
    #pprint(scg.mec_set)
    #MecController.print_mecs(scg.base_station_set, scg.mec_set)
    '''
    while True:
        scg.service_migration('10.0.0.4', '27338475-ceba-4110-acc3-c2e10ffcfe61')
        time.sleep(0.5)
    '''
    #scg.reverse_offloading('10.0.0.4', '48cb9d0e-5c90-46c1-b357-7324123269a1')
    MecController.print_mecs(scg.base_station_set, scg.mec_set)
    while True:
        scg.trade_off()

if __name__=='__main__':
    start_system()


    

