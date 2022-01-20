""" dataclasses modules """
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

""" mec modules """
from mec.mec import MecController

""" vr module """
from vr import HMD

""" onos modules """
from onos import OnosController

""" json encoder module """
from encoder import JsonEncoder

""" other modules """
from munch import DefaultMunch
import os, json

@dataclass 
class VrController:
    """ represents a Vr controller """

    @staticmethod
    def init_vr_users(base_station_set: list, mec_set: list, vr_users: list) -> None:
        files_directory =  './user/'
        file_name = 'users.txt'

        if os.path.isfile('{}{}'.format(files_directory, file_name)):
            return

        users = OnosController.get_hosts()
        for user in users['hosts']:
            new_user = DefaultMunch.fromDict(HMD(ip=user.ipAddresses[0], mac_address=user.mac))
            vr_users.append(new_user)
        
        MecController.init_mobile_services(base_station_set=base_station_set, mec_set=mec_set, vr_users=vr_users)

        new_vr_users = []
        for user in vr_users:
            new_vr_users.append(user.to_dict())

        JsonEncoder.encoder(new_vr_users, files_directory, file_name)

    @staticmethod
    def load_vr_users() -> dict:
        files_directory =  './user/'
        file_name = 'users.txt'
        with open('{}{}'.format(files_directory, file_name)) as json_file:
            data = json.load(json_file)
            result = DefaultMunch.fromDict(data)
            return result 