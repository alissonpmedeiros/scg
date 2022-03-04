import json
import numpy as np

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

    

class JsonEncoder():
    """ provides methods to encode json to file """
    
    @classmethod
    def convert_to_json(data: list) -> list:
        new_data = []
        for item in data:
            new_data.append(item.to_dict())
        return new_data
    
    
    @staticmethod
    def encoder(data, files_directory, file_name):  
        data_json = JsonEncoder.convert_to_json(data)    
        data = json.dumps(data_json, cls=NpEncoder)
        f = open("{}{}".format(files_directory, file_name), "w+")
        f.write(data)
        f.close()
        
            
        