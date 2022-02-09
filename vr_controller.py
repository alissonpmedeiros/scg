""" dataclasses modules """
from dataclasses import dataclass, field

""" vr module """
from vr import HMD, VrService

""" base station module """
from base_station import BaseStationController

""" onos modules """
from onos import OnosController

""" mec modules """
from mec.mec import MecAgent

""" json encoder module """
from encoder import JsonEncoder

""" other modules """
from munch import DefaultMunch, Munch
import orjson as json
import os, random
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

        JsonEncoder.encoder(
            new_vr_users, 
            files_directory, 
            file_name)

    @staticmethod
    def load_vr_users() -> dict:
        print('*** loading vr users ***')
        files_directory =  './user/'
        file_name = 'users.txt'
        with open('{}{}'.format(files_directory, file_name)) as json_file:
            data = json.loads(json_file.read())
            result = DefaultMunch.fromDict(data)
            return result 

    @staticmethod 
    def get_vr_service(
        vr_users: list, 
        user_ip: str, 
        service_id: str) -> dict:
        
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
    def get_vr_user_location(hosts: dict, user_ip: str) -> str:
        """ gets the base station id where the user is connected """
        host = OnosController.get_host(hosts=hosts, host_IP=user_ip)
        user_location = host.locations[0].elementId
        return user_location
    
    @staticmethod
    def remove_vr_service(
        vr_users: list, 
        user_ip: str,  
        service_id: str) -> VrService:
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
    def deploy_vr_service(
        vr_users:list, 
        user_ip: str, 
        service: VrService) -> None:
        for user in vr_users:
            if user.ip == user_ip:
                user.services_set.append(service)
                break

    @staticmethod
    def get_hmd_latency(
        base_station_set: list, 
        vr_users:list, 
        user_ip: str,
        hosts: dict, 
    ) -> float:
        """ gets hmd latency, including the wireless latency where the user is connected to """
        user_location = VrController.get_vr_user_location(hosts=hosts, user_ip=user_ip)
        bs_location = BaseStationController.get_base_station(
            base_station_set=base_station_set, 
            bs_id=user_location)
        user = VrController.get_vr_user(vr_users=vr_users, user_ip=user_ip)

        latency = round(bs_location.wireless_latency + user.computing_latency, 2) 

        return latency
        
    @staticmethod
    def change_quota(service: VrService):
        """ changes a vr service quota """
        quotas_set = ['small', 'tiny', 'medium', 'large', 'xlarge']
        
        """
        choice options to decide whether to change the quota workload or not:
        -1: previous quota from quota_set
         0: nothing changes
         1: next quota from quota_set
        """
        choice = random.randint(-1, 1)
        if choice!= 0:
            quota_name = service.quota.name
            """ gets quota position """
            position = 0
            for quota in quotas_set:
                if quota == quota_name:
                    break
                position +=1

            if choice == -1:
                if position == 0: 
                    """ 
                    can't get the previous quota, because we hitted the first one, then 
                    we go further and get the next quota instead of the previous one 
                    """
                    position = 1
                else:
                    """ otherwise we just get the previous quota position"""
                    position -=1
            else:
                """ 
                can't get the next quota, because we hitted the last one, then 
                we go back and get the previous quota instead of the next one 
                """
                if position == 4:
                    position -=1
                else:
                    """ otherwise we just get the next quota position """
                    position +=1

            """ 
            at this point we know exactly the position of the 
            quota that must replace the current service quota 
            """
            new_quota_name = quotas_set[position]
            new_service = VrService()
            new_quota = DefaultMunch.fromDict(new_service.quota.get_quota(new_quota_name))
            service.quota.name = new_quota_name
            service.quota.resources = new_quota
            
            
    """ NEED TO BE TESTED! """
    @staticmethod
    def check_vr_service_workload(mec_set: list, vr_users: list):
        for user in vr_users:
            for service in user.services_set:
                if service.iterations_count >= service.iterations:
                    VrController.change_quota(service)
                    service.iterations_count = 0
                else:
                    service.iterations_count +=1

    