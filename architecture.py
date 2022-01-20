#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field

from numpy import extract

""" mec modules """
from mec.mec import MecController, MecResources, MecWorkloads, Mec, MecAgent

""" base station modules """
from base_station import BaseStationController

""" graph modules """
from graph import Dijkstra

""" onos modules """
from onos import OnosController

""" vr modules """
from vr import VrService
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
        
        
           

    def calculate_ETE(self, src_location: str, dst_location: str):
        """ calculates the end-to-end latency between two entities """
        
        path, net_latency = Dijkstra.init_algorithm(base_station_set=self.base_station_set, start_node=src_location, target_node=dst_location)

        base_station = BaseStationController.get_base_station(base_station_set=self.base_station_set, bs_id=dst_location)

        mec = MecController.get_mec(mec_set=self.mec_set, mec_id=base_station.mec_id)

        computing_latency = mec.computing_latency 

        ete_latency = net_latency + computing_latency

        #print(" -> ".join(path))
        #print("latency: {}".format(ete_latency))
        return round(ete_latency, 2)

    def service_migration(self):
        """ migrates a service s from mec i to mec j """ 
        for user in self.vr_users:
            for service_id in user.services:
                host = OnosController.get_host(user.ipAddresses[0])
                user_location = host.locations[0].elementId
                
                service_content = MecAgent.get_service(self.mec_set, service_id)
                service_server_id = MecAgent.get_service_server_id(self.mec_set, service_id)
                service_location = MecAgent.get_service_bs_location(self.base_station_set, self.mec_set, service_id)
                previous_service_latency = self.calculate_ETE(src_location=user_location, dst_location=service_location)

                mec_id_candidate = MecController.discover_mec(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_ip=user.ipAddresses[0], service=service_content)

                mec_candidate_location = MecAgent.get_mec_bs_location(self.base_station_set, mec_id_candidate)
                 
                if mec_candidate_location is not None:
                    new_service_latency = self.calculate_ETE(src_location=user_location, dst_location=mec_candidate_location)

                    if new_service_latency < previous_service_latency:
                        extracted_service = MecAgent.remove_service(self.mec_set,  service_server_id, service_id)
                        MecAgent.deploy_service(self.mec_set, mec_id_candidate, extracted_service)
                        print("*** Performing migration ***\n")
                        print("service {} move from MEC {} to {}".format(service_id, service_server_id, mec_id_candidate))
                        print("new latency: {}\n".format(new_service_latency))
                        
                else:
                    print("**** no candidates ****")
                    """ Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation... """

    def offload_services(self):
        for user in self.vr_users:
            for service_id in user.services_ids:
                extract_service = VrController.remove_vr_service(self.vr_users, user.id, service_id)
                mec_id_dst = MecController.discover_mec(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_ip=user.ip, service=extract_service)

                if mec_id_dst is not None:
                    MecAgent.deploy_service(self.mec_set, mec_id_dst, extract_service)
                else:
                    print("could not deploy the following service: {}".format(extract_service))

                #print('service {} moved from HMD {} to mec {} \n'.format(service_id, user.id, mec_id_dst))   

    def reverse_offloading(mec_set: list, service: VrService):
        """ offloads a service i back to vr hmd """ 
        pass      

    def trade_off(self):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""
        pass



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
   
    
    

if __name__=='__main__':
    start_system()


    

