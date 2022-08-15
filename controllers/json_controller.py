"""models modules """
from models.mec import Mec
from models.vr import VrHMD
from models.base_station import BaseStation

""" controller modules """
from controllers import config_controller

""" other modules """
import json, os
from typing import Dict, Any
from munch import DefaultMunch

CONFIG = config_controller.ConfigController.get_config()


class TranscoderController:
    """ provides methods to transcode data """
    
    @staticmethod
    def convert_objects_to_dict(data_set: dict) -> list:
        """ serializes objects to dict from classes that use @dataclass_json """
        
        print(f'\n*** serializing objects to dict***\n')
        for key, value in data_set.items(): 
            data_set[key] = value.to_dict()
    

class EncoderController():
    """ provides methods to encode json data """
    
    @staticmethod
    def encoding_to_json(data_set: Dict[str, Any]) -> None:
        """ encodes a python dict of objects to json objects into a file """
        
        data_directory = CONFIG['SYSTEM']['DATA_DIR']
        
        files_dict = {
            'base_station_set': 'BS_FILE',
            'mec_set': 'MEC_FILE',
            'hmds_set': 'HMDS_FILE'
        }
        
        data_type = next(iter(data_set))
        file_name_option = files_dict.get(data_type)
        file_name = CONFIG['SYSTEM'][file_name_option]
        
        
        if os.path.isfile("{}{}".format(data_directory, file_name)):
            return
            
        TranscoderController.convert_objects_to_dict(data_set[data_type])  
        
        print(f'\n*** encoding***\n')
        with open("{}{}".format(data_directory, file_name), "w+") as file_write:
            json.dump(data_set, file_write, indent=2, ensure_ascii=False)
        
        return 
    

class DecoderController:
    """ provides methods to decoding json data """
    
    @staticmethod
    def decoder_to_dict_objects(data_set: dict, data_type: str) -> None:
        """decodes a dict of json objects into BaseStations, Mecs, or VrHMD objects"""
        
        data_type_dict = {
            'base_station_set': BaseStation,
            'mec_set': Mec,
            'hmds_set': VrHMD
        }
        
        print(f'\n*** decoding {str(data_type_dict[data_type])} objects***')
        
        for key, value in data_set[data_type].items():
            data_type_object = data_type_dict[data_type].from_dict(value)
            data_set[data_type][key] = data_type_object
        
        return 
        
    @staticmethod
    def decoding_to_dict(data_directory: str, file_name: str) -> dict:
        """ decodes a file of json objects into dict of BaseStations, Mecs, or VrHMD objects """
        
        print(f'\n*** decoding -> loading file {data_directory} at {file_name} ***')
        with open("{}{}".format(data_directory, file_name),"r", encoding='utf-8') as json_file:
            data_set = json.load(json_file)
            data_type = next(iter(data_set))
            DecoderController.decoder_to_dict_objects(data_set, data_type)
            return data_set[data_type]
    
    @staticmethod
    def load_to_json_objects(data_set: dict, data_type: str) -> None:
        """loads a dict of json objects into BaseStations, Mecs, or VrHMD objects"""
        
        data_type_dict = {
            'base_station_set': BaseStation,
            'mec_set': Mec,
            'hmds_set': VrHMD
        }
        
        #print(f'\n*** loading {str(data_type_dict[data_type])} objects***')
        
        for key, value in data_set[data_type].items():
            data_type_object = data_type_dict[data_type].from_json(value)
            data_set[data_type][key] = data_type_object
        
        return 
    
    @staticmethod
    def loading_to_dict(data_set: Dict[str,str]) -> dict:
        """ loads a dict of str into dict of BaseStations, Mecs, or VrHMD objects based on data_type """
    
        data_type = next(iter(data_set))
        DecoderController.load_to_json_objects(data_set, data_type)
        return data_set[data_type]
    
    
    @staticmethod
    def decode_net_config_file() -> dict:
        """ decodes network configuration file """
        
        data_directory = CONFIG['NETWORK']['NETWORK_FILE_DIR']
        file_name = CONFIG['NETWORK']['NETWORK_FILE']
        
        print(f'\n*** loading file {file_name} at {data_directory} ***')
        
        with open("{}{}".format(data_directory, file_name)) as json_file:
            data = json.loads(json_file.read())
            result = DefaultMunch.fromDict(data)
            return result
        
        
       