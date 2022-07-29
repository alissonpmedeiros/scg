import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 

from models.base_station import BaseStation 

""" controller modules """
from controllers import onos_controller as onos
from controllers import json_controller as json

"""other modules"""
import random
from typing import List
from munch import DefaultMunch

class BaseStationController:
    """ represents a base station controller """
    
    @staticmethod
    def get_base_station(base_station_set: List[BaseStation], bs_id: str) -> BaseStation:
        for base_station in base_station_set:
            if base_station.id == bs_id:
                return base_station
        return None            
            
    @staticmethod
    def get_base_station_by_name(base_station_set: List[BaseStation], bs_name: str) -> BaseStation:
        for base_station in base_station_set:
            if base_station.name == bs_name:
                return base_station
        return None
    
    @staticmethod
    def print_base_stations(base_station_set: List[BaseStation]) -> None:
        for base_station in base_station_set:
            print(f'\nid: {base_station.id}')
            print(f'name: {base_station.name}')
            print(f'links:')
            for key, value in base_station.links.items():
                print(f'dst: {key} -> [{value["latency"]}]')   
        return
        
    @staticmethod
    def set_bs_net_latency(base_station_set: list) -> None:
        """ generates the network latency for base station i"""
        network_config = json.DecoderController.decode_net_config_file()
            
        from pprint import pprint as pprint
        for base_station in base_station_set:
            device_name = base_station.name[2:]
            device_id = int(device_name)
            device = onos.OnosController.get_device_from_file(devices=network_config, device_id=device_id)
            
            for destination, link_latency in zip(device['edges'], device['edge_distances']):    
                dst_bs_name = 'BS' + str(destination)
                dst_bs = BaseStationController.get_base_station_by_name(base_station_set, dst_bs_name)
                base_station.links[dst_bs.id]['latency'] = link_latency
                # ensures that A to B has the same latency of B to A
                dst_bs.links[base_station.id]['latency'] = link_latency 
        return 
            
    @staticmethod
    def init_base_stations(mec_set: List['Mec']) -> None:
        """ builds base station topology based on the network topology built by ONOS """
        
        base_station_set = []
        bs_topology = onos.OnosController.get_topology()

        for base_station in bs_topology:    
            bs_links = {}
            for link in base_station.links:
                dst_id = link.dst.device
                dst_port = link.dst.port
                dst_latency = None
                bs_links[dst_id] = {
                    'port': dst_port,
                    'latency': dst_latency
                }  
            mec_index = int(base_station.name[2:])
            new_base_station = DefaultMunch.fromDict(
                BaseStation(
                    id=base_station.id, 
                    name=base_station.name, 
                    mec_id=mec_set[mec_index].id, 
                    links=DefaultMunch.fromDict(bs_links)
                )
            )    
            
            base_station_set.append(new_base_station)
            
        BaseStationController.set_bs_net_latency(base_station_set=base_station_set)
        json.EncoderController.encoding_to_json(data_set=base_station_set)
        return

   