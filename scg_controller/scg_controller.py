#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field

""" onos controller modules """
from sdn.onos import OnosController

""" mec modules """
from mec.mec import Mec
from mec.mec_agent import MecAgent
from mec.mec_controller import MecController

""" base station modules """
from base_station.bs_controller import BaseStation, BaseStationController

""" graph modules """
from graph.dijkstra import DijkstraController
from graph.graph import Graph, GraphController

""" vr controller modules """
from vr.vr_hmd import VrHMD
from vr.vr_controller import VrController

""" other modules """
from typing import List
from pprint import pprint as pprint
import time, json, os, random


@dataclass
class ScgController:
    """ SCG controller representation """

    services_per_user = 1
    overall_mecs: int = field(default=28)
    graph: Graph = field(init=False)
    onos: OnosController = field(init=False)
    mec_set: List[Mec] = field(default_factory=list, init=False)
    vr_users: List[VrHMD] = field(default_factory=list, init=False)
    base_station_set: List[BaseStation] = field(default_factory=list, init=False)

    def __post_init__(self):
        """starting onos sdn controller instance"""
        self.onos=OnosController()
        
        """starting mecs, base stations, and vr users"""
        MecController.init_mec_servers(self.overall_mecs)
        self.mec_set = MecController.load_mec_servers()
        
        BaseStationController.init_base_stations(mec_set=self.mec_set)
        VrController.init_vr_users(services_per_user=self.services_per_user)
        
        """loading mecs, base stations, and vr users files"""
        self.base_station_set = BaseStationController.load_base_stations()
        self.vr_users = VrController.load_vr_users()
        
        """init graph with all sources and destinations nodes """
        self.graph = GraphController.get_graph(self.base_station_set, self.mec_set)
        
        """initially offloads all services to the network edge"""
        self.offload_services()

    def get_average_E2E_latency(self):
        total_latency = 0
        total_net_latency = 0
        total_computing_latency = 0
        services_cont = 0
        for user in self.vr_users:
            for service_id in user.services_ids:
                if any(service_id == service.id for service in user.services_set):
                    """ checks whether a service IS deployed on the HMD """

                    hmd_latency = VrController.get_hmd_latency(
                        base_station_set=self.base_station_set,
                        vr_users=self.vr_users,
                        user_ip=user.ip,
                    )
                    total_computing_latency+=hmd_latency
                    total_latency += hmd_latency
                
                else:
                    """ otherwise, the service is deployed on MEC servers"""

                    service_location = MecAgent.get_service_bs_id(
                        self.base_station_set, self.mec_set, service_id
                    )

                    """ 
                    measures the latency between bs where the user is 
                    connected and the mec where the service is deployed 
                    """
                    network_latency, computing_latency, ete_latency = ScgController.get_E2E_latency(
                        base_station_set=self.base_station_set,
                        mec_set=self.mec_set,
                        src_location=user.current_location,
                        dst_location=service_location,
                        graph=self.graph,
                    )
                    total_net_latency += network_latency
                    total_computing_latency+=computing_latency
                    total_latency += ete_latency

                
                services_cont += 1
        
        average_net_latency = round((total_net_latency / services_cont), 3)
        average_computing_latency = round((total_computing_latency / services_cont), 3)
        average_latency = round((total_latency / services_cont), 3)
        return average_net_latency, average_computing_latency, average_latency

    @staticmethod
    def get_E2E_latency(
        base_station_set: List[BaseStation], mec_set: List[Mec], src_location: str, dst_location: str, graph: Graph
    ) -> float:
        """
        calculates the end-to-end latency between a vr
        user and the mec where the service is deployed on
        """
        src_bs = BaseStationController.get_base_station(
            base_station_set, src_location
        )
        src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
        path, ete_latency = DijkstraController.get_shortest_path(
            start_node=src_location,
            start_node_computing_delay=src_mec.computing_latency,
            start_node_wireless_delay=src_bs.wireless_latency,
            target_node=dst_location,
            graph=graph
        )
        base_station = BaseStationController.get_base_station(
            base_station_set=base_station_set, 
            #gets last element of the path, which corresponds to the base station destination with the optimal mec service in terms of latency"""
            bs_id=path[-1] 
        )
        mec = MecController.get_mec(mec_set, base_station.mec_id)
        
        computing_latency = mec.computing_latency 
        network_latency = ete_latency - computing_latency
        return network_latency, computing_latency, ete_latency

    def offload_services(self) -> None:
        for user in self.vr_users:
            for service_id in user.services_ids:
                extracted_service = VrController.remove_vr_service(
                    vr_users=self.vr_users, user_ip=user.ip, service_id=service_id
                )

                mec_id_dst = MecController.discover_mec(
                    base_station_set=self.base_station_set,
                    mec_set=self.mec_set,
                    user=user,
                    service=extracted_service,
                    graph=self.graph
                )

                if mec_id_dst is not None:
                    MecAgent.deploy_service(self.mec_set, mec_id_dst, extracted_service)
                else:
                    print(
                        "could not OFFLOAD the following service: {}".format(
                            extracted_service
                        )
                    )

    def calculate_gpu_usage(self) -> float:
        total_services = len(self.vr_users)
        total_gpus = 0

        for user in self.vr_users:
            for service in user.services_set:
                total_gpus += service.quota.resources.gpu

        for mec in self.mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    total_gpus += service.quota.resources.gpu

        result = total_gpus / total_services
        #print('total services: {} | total gpus: {}'.format(total_services, total_gpus))
        #time.sleep(1)
        return result

    
    def get_vr_services_on_HMD(self)-> int:
        count  = 0
        for user in self.vr_users:
            for service in user.services_set:
                count +=1
        return count