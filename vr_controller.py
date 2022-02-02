""" dataclasses modules """
from dataclasses import dataclass, field

""" vr module """
from vr import HMD, VrService

""" base station module """
from base_station import BaseStationController

""" onos modules """
from onos import OnosController

""" json encoder module """
from encoder import JsonEncoder

""" other modules """
from munch import DefaultMunch
import os, json
from pprint import pprint as pprint
@dataclass 
class VrController:
    """ represents a Vr controller """

    @staticmethod
    def init_vr_users(services_per_user: int) -> None:
        vr_users = []
        new_vr_users = []
        files_directory =  '/home/ubuntu/scg/user/'
        file_name = 'users.txt'

        if os.path.isfile('{}{}'.format(files_directory, file_name)):
            return

        users = OnosController.get_hosts()
        for user in users['hosts']:
            new_user = DefaultMunch.fromDict(HMD(ip=user.ipAddresses[0], mac_address=user.mac))

            for i in range(0, services_per_user):
                new_service = VrService(is_mobile=True)
                new_user.services_set.append(new_service)
                new_user.services_ids.append(new_service.id)
            
            vr_users.append(new_user)
            
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

    @staticmethod 
    def get_vr_service(vr_users: list, user_ip: str, service_id: str) -> dict:
        
        for user in vr_users:
            if user.ip == user_ip:
                for service in user.services_set:
                    if service.id == service_id:
                        return service

    @staticmethod
    def get_vr_user(vr_users: list, user_ip: str) -> dict:
        for user in vr_users:
            if user.ip == user_ip:
                return user

    @staticmethod 
    def get_vr_user_location(user_ip: str) -> str:
        """ gets the base station id where the user is connected """
        host = OnosController.get_host(user_ip)
        user_location = host.locations[0].elementId
        return user_location
    
    @staticmethod
    def remove_vr_service(vr_users: list, user_ip: str,  service_id: str) -> VrService:
        """ removes a service from where it is deployed """
        extracted_service = None
        service_index = 0
        for user in vr_users:
            if user.ip == user_ip:
                for service in user.services_set:
                    if service.id == service_id:
                        break
                    service_index += 1
                extracted_service = user.services_set.pop(service_index)
                break
        return extracted_service

    @staticmethod
    def deploy_vr_service(vr_users:list, user_ip: str, service: VrService) -> None:
        for user in vr_users:
            if user.ip == user_ip:
                user.services_set.append(service)
                break

    @staticmethod
    def get_hmd_latency(base_station_set: list, vr_users:list, user_ip: str) -> float:
        """ gets hmd latency, including the wireless latency where the user is connected to """
        user_location = VrController.get_vr_user_location(user_ip=user_ip)
        bs_location = BaseStationController.get_base_station(base_station_set=base_station_set, bs_id=user_location)
        user = VrController.get_vr_user(vr_users=vr_users, user_ip=user_ip)

        latency = round(bs_location.wireless_latency + user.computing_latency, 2) 

        return latency