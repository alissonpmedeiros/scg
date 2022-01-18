#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field
from importlib.metadata import files

""" mec modules """
from mec.mec import MecController, MecResources, MecWorkloads, Mec, MecAgent

""" base station modules """
from base_station import BaseStationController

""" graph modules """
from graph import Dijkstra

""" onos modules """
from onos import OnosController

""" vr modules """
from vr import VrService, VrAgent

""" other modules """
from typing import List
from pprint import pprint as pprint   
import time


@dataclass
class ScgController:
    """ SCG controller representation """
    overall_mecs: int = field(default = 100)
    base_station_set: List[dict] = field(default_factory=list, init=False)
    mec_set: List[Mec] = field(default_factory=list, init=False)
    vr_users: List[list] = field(default_factory=list, init=False)


    def __post_init__(self):
        self.mec_set = MecController.load_mec_servers()
        MecController.build_mec_topology(self.base_station_set, self.mec_set)
        BaseStationController.set_bs_net_latency(self.base_station_set)
        self.get_vr_users()
        MecController.init_mobile_services(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_users=self.vr_users)
        
        
    def get_vr_users(self) -> None:
        users = OnosController.get_hosts()
        for user in users['hosts']:
            user['services'] = []
            self.vr_users.append(user)


    def calculate_ETE(self, src_location: str, dst_location: str):
        """ calculates the end-to-end latency between two entities """
        
        path, ete_latency = Dijkstra.init_algorithm(base_station_set=self.base_station_set, start_node=src_location, target_node=dst_location)

        #print(" -> ".join(path))
        #print("latency: {}".format(ete_latency))
        return round(ete_latency, 2)
    

    def check_migration(self):
        for user in self.vr_users:
            for service_id in user.services:
                host = OnosController.get_host(user.ipAddresses[0])
                user_location = host.locations[0].elementId
                
                service_content = MecAgent.get_service(self.mec_set, service_id)
                service_server_id = MecAgent.get_service_server_id(self.mec_set, service_id)
                service_location = MecAgent.get_service_bs_location(self.base_station_set, self.mec_set, service_id)
                previous_service_latency = self.calculate_ETE(user_location, service_location)

                mec_id_candidate = MecController.discover_mec(base_station_set=self.base_station_set, mec_set=self.mec_set, vr_ip=user.ipAddresses[0], service=service_content)

                mec_candidate_location = MecAgent.get_mec_bs_location(self.base_station_set, mec_id_candidate)
                 
                if mec_candidate_location is not None:
                    new_service_latency = self.calculate_ETE(user_location, mec_candidate_location)

                    if new_service_latency < previous_service_latency:
                        extracted_service = MecAgent.remove_service(self.mec_set,  service_server_id, service_id)
                        MecAgent.deploy_service(self.mec_set, mec_id_candidate, extracted_service)
                        print("*** Performing migration ***\n")
                        print("service {} move from MEC {} to {}\n".format(service_id, service_server_id, mec_id_candidate))
                        
                else:
                    print("**** no candidates ****")
                    """ Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation... """
                    
                

    def trade_off(self):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""
        pass



def start_system() -> None:
    scg = ScgController()
    #scg.print_mecs()
    #pprint(scg.vr_users)
    #print("\n")
    #a = input("start check migration!")
    while True:
        print("\n\n##############################\n")
        scg.check_migration()
        time.sleep(1)
        
    

if __name__=='__main__':
    start_system()


    

