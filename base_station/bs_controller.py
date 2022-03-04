#!/user/bin/python3

""" onos sdn controller module """
from sdn.onos import OnosController

""" base station module """
from base_station.base_station import BaseStation

""" np incoder module"""
from encoders.json_encoder import JsonEncoder

"""other modules"""
from typing import List
import random, json, os
from munch import DefaultMunch
from pprint import pprint as pprint
from mec.mec import Mec


     

class BaseStationController:

    @staticmethod
    def get_base_station(base_station_set: List[BaseStation], bs_id: str) -> BaseStation:
        for base_station in base_station_set:
            if base_station.id == bs_id:
                return base_station

    @staticmethod
    def generate_bs_latency_keys(base_station_set) -> None:
        """ creates dict keys on each base station data structure """
        for base_station in base_station_set:
            for link in base_station.links:
                link['latency'] = 0.0

    @staticmethod
    def set_destination_latency(
        base_station_set: List[BaseStation], 
        src_id: str, 
        dst_id: str, 
        latency: float) -> None:
        """ sets the same latency of the source node on the destination node """
        for base_station in base_station_set:
            for link in base_station.links:
                """ 
                the test occurs in a inverse way (src with dst) because we have to make sure that 
                only a unique link that belongs to a base station will have the same 'latency' parameter 
                """
                if link.src.device == dst_id and link.dst.device == src_id:
                    link.latency = latency
                    break
    
    @staticmethod
    def set_bs_net_latency(base_station_set) -> None:
        """ generates the network latency for base station i"""
        BaseStationController.generate_bs_latency_keys(base_station_set)
        
        for base_station in base_station_set:
            """ includes the delay on each base station destination """
            for link in base_station.links:
                """ generates the network latencty randomly """
                net_latency = round(random.uniform(0.5, 1), 2)    
                link.latency = net_latency
                
                """ makes sure that A to B has the same delay of B to A"""
                BaseStationController.set_destination_latency(
                    base_station_set=base_station_set, 
                    src_id=base_station.id, 
                    dst_id=link.dst.device, 
                    latency=net_latency)

    @staticmethod
    def save_base_stations_to_file(base_station_set: List[BaseStation]) -> None:
        files_directory = "/home/ubuntu/scg/base_station/"
        file_name_servers = "base_stations.json"
        
        if os.path.isfile("{}{}".format(files_directory, file_name_servers)):
            return
        
        """ encoding json to txt file """
        JsonEncoder.encoder(base_station_set, files_directory, file_name_servers)
    
    @staticmethod
    def init_base_stations(mec_set: List[Mec]) -> None:
        """ builds MEC topology based on the network topology built by ONOS """
        
        base_station_set = []

        """ gets base stations topology from onos """
        bs_topology = OnosController.get_topology()
        i = 0

        for node in bs_topology:    
            """ gets a mec server id and stores it on the base station object"""
            '''
            print(node.id)
            print(node.name)
            print(mec_set[i].id)
            print(node.links)
            print('\n\n')
            a = input('')
            '''
            base_station = DefaultMunch.fromDict(BaseStation(id=node.id, name=node.name, mec_id=mec_set[i].id, links=DefaultMunch.fromDict(node.links))) 
            base_station_set.append(base_station)
            i+=1
            
        BaseStationController.set_bs_net_latency(base_station_set=base_station_set)
        
        BaseStationController.save_base_stations_to_file(base_station_set=base_station_set)
        
    @staticmethod
    def load_base_stations() -> dict:
        print("*** loading base stations servers ***")
        files_directory = "/home/ubuntu/scg/base_station/"
        file_name_servers = "base_stations.json"
        with open("{}{}".format(files_directory, file_name_servers)) as json_file:
            data = json.loads(json_file.read())
            result = DefaultMunch.fromDict(data)
            return result
        
   