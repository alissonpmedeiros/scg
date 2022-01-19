#!/user/bin/python3

""" onos sdn controller module """
from onos import OnosController

import random

class BaseStationController:

    @staticmethod
    def get_base_station(base_station_set: list, bs_id: str) -> dict:
        for base_station in base_station_set:
            if base_station.id == bs_id:
                return base_station

    @staticmethod
    def generate_bs_latency_keys(base_station_set):
        """ creates dict keys on each base station data structure """
        for base_station in base_station_set:
            base_station['wireless_latency'] = round(random.uniform(0.1, 0.3), 2) 
            for link in base_station.links:
                link['latency'] = 0.0
                #link['wireless_latency'] = round(random.uniform(0.1, 0.3), 2)  

    @staticmethod
    def set_destination_latency(base_station_set, src_id, dst_id, latency: float) -> None:
        """ sets the same latency of the source node on the destination node """
        for base_station in base_station_set:
            for link in base_station.links:
                """ 
                the test occurs in a inverse way (src with dst) because we have to make sure that only a unique link that belongs to a base station will have the same 'latency' parameter 
                """
                if link.src.device == dst_id and link.dst.device == src_id:
                    link.latency = latency
                    break
    
    @staticmethod
    def set_bs_net_latency(base_station_set):
        """ generates the network latency for base station i"""
        BaseStationController.generate_bs_latency_keys(base_station_set)
        
        for base_station in base_station_set:
            """ includes the delay on each base station destination """
            for link in base_station.links:
                """ generates the network latencty randomly """
                net_latency = round(random.uniform(0.1, 1), 2)    
                link.latency = net_latency
                
                """ makes sure that A to B has the same delay of B to A"""
                BaseStationController.set_destination_latency(base_station_set=base_station_set, src_id=base_station.id, dst_id=link.dst.device, latency=net_latency)

    @staticmethod
    def build_network_topology(base_station_set: list, mec_set: list) -> None:
        """ builds MEC topology based on the network topology built by ONOS """

        """ gets base stations topology from onos """
        bs_topology = OnosController.get_topology()
        total_mecs_without_gpus = int(len(bs_topology) * 0.2)
        mecs_without_gpus = 0
        i = 0

        for base_station in bs_topology:
            """ if-else statement controls how many mec servers without gpus must exist in the system (20%) """
            if mec_set[i].overall_gpu == 0 and mecs_without_gpus < total_mecs_without_gpus:
                mecs_without_gpus += 1
            else:
                while True:
                    i+=1
                    if mec_set[i].overall_gpu != 0:
                        break
            
            """ gets a mec server id and stores it on the base station object"""
            base_station['mec_id'] = mec_set[i].id 
            base_station_set.append(base_station)
            i+=1
        
        BaseStationController.set_bs_net_latency(base_station_set=base_station_set)