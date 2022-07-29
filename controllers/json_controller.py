""" controller modules """
from controllers import config_controller as config

""" other modules """
import json, os
import numpy as np
from munch import DefaultMunch

class NpEncoder(json.JSONEncoder):
    """ converting NumPy numbers to a Python int before serializing the objec """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class TranscoderController:
    """ provides methods to transcode data """
    
    @staticmethod
    def convert_to_dict(data: list) -> list:
        """ converts a list to dict """
        new_data = []
        for item in data:
            new_data.append(item.to_dict())
        return new_data
    

class EncoderController():
    """ provides methods to encode json data """
    
    @staticmethod
    def encoder(data: list, data_directory: str, file_name: str) -> None:  
        data_json = TranscoderController.convert_to_dict(data)    
        data = json.dumps(data_json, cls=NpEncoder)
        f = open("{}{}".format(data_directory, file_name), "w+")
        f.write(data)
        f.close()
        
            
    @staticmethod
    def encoding_to_json(data_set: list) -> None:
        """ encodes a list to json file """
        
        '''#TODO: test the commented method in order to replace the encoder method
        CONFIG = ConfigController.get_config()
        data_directory = CONFIG['SYSTEM']['DATA_DIR']
        
        files_dict = {
            'BaseStation': 'BS_FILE',
            'Mec': 'MEC_FILE',
            'VrHMD': 'USERS_FILE'
        }
        
        data_type = type(data_set[0]).__name__
        file_name = files_dict.get(data_type)'''
        
        
        CONFIG = config.ConfigController.get_config()
        data_directory = CONFIG['SYSTEM']['DATA_DIR']
        file_name = ''
        
        if type(data_set[0]).__name__ == 'BaseStation':
            file_name = CONFIG['SYSTEM']['BS_FILE']
        elif type(data_set[0]).__name__ == "Mec":
            file_name = CONFIG['SYSTEM']['MEC_FILE']
        else:
            file_name = CONFIG['SYSTEM']['USERS_FILE']
    
        if os.path.isfile("{}{}".format(data_directory, file_name)):
            #print(f'*** file {file_name} at {data_directory} already exists! ***')
            return
        
        """ encoding to json file """
        EncoderController.encoder(data=data_set, data_directory=data_directory, file_name=file_name)


class DecoderController:
    """ provides methods to decoding json data """
    
    def decoding_to_dict(data_dir: str, file_name: str) -> dict:
        """ decodes a json file to dict """
        
        print(f'*** loading file {file_name} at {data_dir} ***')
        
        with open("{}{}".format(data_dir, file_name)) as json_file:
            data = json.loads(json_file.read())
            result = DefaultMunch.fromDict(data)
            return result
    
    def decode_net_config_file() -> dict:
        """ decodes network configuration file """
        
        CONFIG = config.ConfigController.get_config()
        data_directory = CONFIG['NETWORK']['NETWORK_FILE_DIR']
        file_name = CONFIG['NETWORK']['NETWORK_FILE']
        return DecoderController.decoding_to_dict(data_dir=data_directory, file_name=file_name)