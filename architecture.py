#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field

""" mec modules """
from mec.mec import Mec, MecAgent
from mec.mec_controller import MecController

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
    services_per_user = 1
    overall_mecs: int = field(default = 28)
    base_station_set: List[dict] = field(default_factory=list, init=False)
    mec_set: List[Mec] = field(default_factory=list, init=False)
    vr_users: List[list] = field(default_factory=list, init=False)


    def __post_init__(self):
        MecController.init_servers(self.overall_mecs)
        self.mec_set = MecController.load_mec_servers()
        BaseStationController.build_network_topology(
            base_station_set=self.base_station_set, 
            mec_set=self.mec_set)
        
        VrController.init_vr_users(services_per_user=self.services_per_user)
        self.vr_users = VrController.load_vr_users()
        
        self.offload_services()

    def caculate_average_ETE(self):
        total_latency = 0
        services_cont = 0
        for user in self.vr_users:
            for service_id in user.services_ids:
                user_location = VrController.get_vr_user_location(user_ip=user.ip)
                if any (service['id'] == service_id for service in user.services_set):    
                    """ checks whether a service IS deployed on the HMD """

                    hmd_latency = VrController.get_hmd_latency(base_station_set=self.base_station_set, vr_users=self.vr_users, user_ip=user.ip)
                    total_latency += hmd_latency
                else:
                    """ otherwise, the service is deployed on MEC servers"""
                    service_location = MecAgent.get_service_bs_location(
                        self.base_station_set, 
                        self.mec_set, 
                        service_id)
                    
                    """ 
                    measures the latency between bs where the user is 
                    connected and the mec where the service is deployed 
                    """
                    current_service_latency = ScgController.calculate_ETE(
                        base_station_set=self.base_station_set, 
                        mec_set=self.mec_set, 
                        src_location=user_location, 
                        dst_location=service_location)

                    total_latency += current_service_latency
                
                services_cont += 1
        
        average_latency = total_latency/services_cont
        return average_latency

    @staticmethod           
    def calculate_ETE(
        base_station_set: list, 
        mec_set: list, 
        src_location: str, 
        dst_location: str) -> float:
        """ 
        calculates the end-to-end latency between a vr 
        user and the mec where the service is deployed on 
        """
        
        path, net_latency = Dijkstra.init_algorithm(
            base_station_set=base_station_set, 
            start_node=src_location, 
            target_node=dst_location)

        base_station = BaseStationController.get_base_station(
            base_station_set=base_station_set, 
            bs_id=dst_location)

        mec = MecController.get_mec(
            mec_set=mec_set, 
            mec_id=base_station.mec_id)

        computing_latency = mec.computing_latency 

        ete_latency = net_latency + computing_latency

        #print(" -> ".join(path))
        #print("latency: {}".format(ete_latency))
        return round(ete_latency, 2)

    def offload_services(self) -> None:
        for user in self.vr_users:
            for service_id in user.services_ids:
                extract_service = VrController.remove_vr_service(
                    vr_users=self.vr_users, 
                    user_ip=user.ip, 
                    service_id=service_id)
                
                mec_id_dst = MecController.discover_mec(
                    base_station_set=self.base_station_set, 
                    mec_set=self.mec_set, 
                    vr_ip=user.ip, 
                    service=extract_service)

                if mec_id_dst is not None:
                    MecAgent.deploy_service(
                        self.mec_set, 
                        mec_id_dst, 
                        extract_service)
                else:
                    print("could not OFFLOAD the following service: {}".format(extract_service))


    def calculate_gpu_usage(self) -> float:
        total_services = 0
        total_gpus = 0

        
        for user in self.vr_users:
            total_services += len(user.services_ids)
            for service in user.services_set:
                total_gpus += service.quota.resources.gpu
                
            
        for mec in self.mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    total_gpus += service.quota.resources.gpu
        
        
        result = (round(total_gpus /  total_services), 2)
        return result                
    
    def calculate_migration_rate(self) -> None:
        pass

              
   
    
        






    

