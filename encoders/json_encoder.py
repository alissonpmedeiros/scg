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
    """ encoding json to txt file """
    @staticmethod
    def encoder(mec_set, files_directory, file_name):    
        mecs = json.dumps(mec_set, cls=NpEncoder)
        f = open("{}{}".format(files_directory, file_name), "w+")
        f.write(mecs)
        f.close()