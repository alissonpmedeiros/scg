import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 

from models.base_station import BaseStation 

""" controller modules """
from controllers import onos_controller
from controllers import json_controller

"""other modules"""
import random
from typing import Dict
from munch import DefaultMunch


class BaseStationController:
    """ represents a base station controller """
    
    @staticmethod
    def get_base_station(base_station_set: Dict[str, BaseStation], bs_id: str) -> BaseStation:
        """gets a base station by ID"""
        
        return base_station_set[bs_id]
                   
    @staticmethod
    def get_base_station_by_name(base_station_set: Dict[str, BaseStation], bs_name: str) -> Dict[str, BaseStation]:
        """gets the base station by name and returns its ID and its object"""
        
        bs_dict: Dict[str, BaseStation] = {
            'id': None,
            'base_station': None
        }
        
        for bs_id, base_station in base_station_set.items():
            if base_station.name == bs_name:
                bs_dict.update({'id': bs_id, 'base_station': base_station})
                break
        
        return bs_dict
    
    @staticmethod
    def print_base_stations(base_station_set: Dict[str, BaseStation]) -> None:
        for bs_id, base_station in base_station_set.items():
            print(f'\nid: {bs_id}')
            print(f'name: {base_station.name}')
            print(f'links:')
            for key, value in base_station.links.items():
                print(f'dst: {key} -> [{value["latency"]}]')   
        return
        
    @staticmethod
    def set_bs_net_latency(base_station_set: dict) -> None:
        """ generates the network latency for base station i"""
        network_config = json_controller.DecoderController.decode_net_config_file()
        
        for bs_id, base_station in base_station_set.items():
            device_name = base_station.name[2:]
            device_id = int(device_name)
            device = onos_controller.OnosController.get_device_from_file(network_config, device_id)
            
            for destination, link_latency in zip(device['edges'], device['edge_distances']):    
                dst_bs_name = 'BS' + str(destination)
                dst = BaseStationController.get_base_station_by_name(base_station_set, dst_bs_name)
                dst_bs_id: str = dst.get('id')
                dst_bs: BaseStation = dst.get('base_station')
                base_station.links[dst_bs_id]['latency'] = link_latency
                # ensures that A to B has the same latency of B to A
                dst_bs.links[bs_id]['latency'] = link_latency 
      
        return 
            
    @staticmethod
    def init_base_stations(mec_set: Dict[str,'Mec']) -> None:
        """ builds base station topology based on the network topology built by ONOS """
        
        mec_keys = []
        mec_names = []
        
        for key, value in mec_set.items():
            mec_keys.append(key)
            mec_names.append(value.name)
        
        
        base_station_set = {
            "base_station_set": {}
        }
        
        bs_topology = onos_controller.OnosController.get_topology()
        mec_index = 0
        
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
                
            mec_name = 'MEC' + base_station.name[2:]
            mec_index = mec_names.index(mec_name)
            
            new_base_station_id = base_station.id
            new_base_station = BaseStation(
                    name = base_station.name, 
                    mec_id = mec_keys[mec_index], 
                    wireless_latency = round(random.uniform(0.1, 0.3), 2),
                    links = DefaultMunch.fromDict(bs_links)
                )
            base_station_set['base_station_set'][new_base_station_id] = new_base_station
        
            
        BaseStationController.set_bs_net_latency(base_station_set['base_station_set'])
        json_controller.EncoderController.encoding_to_json(base_station_set)
        return

   