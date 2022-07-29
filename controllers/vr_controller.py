import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.base_station import BaseStation
    
from models.vr import VrHMD 
from models.vr import VrService 
from models.vr import ServiceQuota

""" controller modules """
from controllers import bs_controller as bs
from controllers import onos_controller as onos
from controllers import json_controller as json
from controllers import config_controller as config

""" other modules """
import random
from typing import List
from munch import DefaultMunch
from dataclasses import dataclass

@dataclass 
class VrController:
    """ represents a Vr controller """
    
    @staticmethod
    def generate_hmd_latency():
        CONFIG = config.ConfigController.get_config()
        lower_latency_threshold = CONFIG['HMDS']['LOWER_LATENCY_THRESHOLD']
        upper_latency_threshold = CONFIG['HMDS']['UPPER_LATENCY_THRESHOLD']
        computing_latency = round(random.uniform(lower_latency_threshold, upper_latency_threshold), 2)
        return computing_latency

    @staticmethod
    def init_vr_users(services_per_user: int) -> None:
        """ inits vr users """
        
        vr_users = []
        users = onos.OnosController.get_hosts()
        for user in users['hosts']:
            new_user = DefaultMunch.fromDict(
                VrHMD(
                    ip=user.ipAddresses[0], 
                    mac_address=user.mac,
                    previous_location=user.locations[0].elementId,
                    current_location=user.locations[0].elementId,
                    computing_latency=VrController.generate_hmd_latency()
                    )
            )

            for i in range(0, services_per_user):
                new_service = VrService(is_mobile=True)
                new_user.services_set.append(new_service)
                new_user.services_ids.append(new_service.id)
            
            vr_users.append(new_user)
            
        json.EncoderController.encoding_to_json(data_set=vr_users)


    @staticmethod 
    def get_vr_service(
        vr_users: List[VrHMD], 
        user_ip: str, 
        service_id: str) -> dict:
        
        for user in vr_users:
            if user.ip == user_ip:
                for service in user.services_set:
                    if service.id == service_id:
                        return service
        return None

    @staticmethod 
    def get_vr_service_owner(vr_users: List[VrHMD], service: VrService) -> VrHMD:
        for user in vr_users:
            for service_id in user.services_ids:
                if service_id == service.id:
                    return user

        return None

    @staticmethod
    def get_vr_user(vr_users: List[VrHMD], user_ip: str) -> VrHMD:
        for user in vr_users:
            if user.ip == user_ip:
                return user
        return None

    
    @staticmethod
    def remove_vr_service(vr_hmd: VrHMD, service_id: str) -> VrService:
        """ removes a service from where it is deployed """
        extracted_service = None
        service_index = [vr_service.id for vr_service in vr_hmd.services_set].index(service_id)
        #print(f'new index: {service_index}')
        extracted_service = vr_hmd.services_set.pop(service_index)
        '''
        service_index = 0
        for hmd in vr_hmds:
            if hmd.ip == vr_hmd.ip:
                for service in hmd.services_set:
                    if service.id == service_id:
                        break
                    service_index += 1
                print(f'original index: {service_index}')
                
                    
                a = input('')
                extracted_service = hmd.services_set.pop(service_index)
                break
        '''
        return extracted_service

    @staticmethod
    def deploy_vr_service(
        vr_users: List[VrHMD], user_ip: str, service: VrService
    ) -> None:
        for user in vr_users:
            if user.ip == user_ip:
                user.services_set.append(service)
                break

    @staticmethod
    def get_hmd_latency(
        base_station_set: List['BaseStation'], vr_users: List[VrHMD], user_ip: str,
    ) -> float:
        """ gets hmd latency, including the wireless latency where the user is connected to """
        user = VrController.get_vr_user(vr_users=vr_users, user_ip=user_ip)
        bs_location = bs.BaseStationController.get_base_station(
            base_station_set=base_station_set, 
            bs_id=user.current_location)
        user = VrController.get_vr_user(vr_users=vr_users, user_ip=user_ip)

        latency = round(bs_location.wireless_latency + user.computing_latency, 2) 

        return latency
        
    @staticmethod # TODO: CHECK THIS NEW METHOD IMPLENTATION
    def change_quota(service: VrService):
        """ changes a vr service quota """
        quotas_set = ServiceQuota.get_quotas_set()
        
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
            position = quotas_set.index(quota_name)

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
                can't get the next quota, because we hitted the last one, 
                instead we go back and get the previous quota  
                """
                if position == len(quotas_set) - 1:
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
            

    '''
    @staticmethod
    def change_quota(service: VrService):
        """ changes a vr service quota """
        quotas_set = ServiceQuota.get_quotas_set()
        
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
                if position == len(quotas_set) - 1:
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
    '''


    """
    @staticmethod
    def change_resolution(service: VrService): 
        
        service_e2e_latency = 10
        resolution_type = None
        
        if service_e2e_latency <= 3:
            resolution_type = '8k'
        elif service_e2e_latency > 3 and service_e2e_latency <= 3.5:
            resolution_type = '4k'
        elif service_e2e_latency > 3.5 and service_e2e_latency <= 4:
            resolution_type = '1440p'
        else:
            resolution_type = '1080p'
        
        resolution = DecoderResolution(resolution_type)
        decoder = Decoder(resolution)
        service.decoder.resolution.name = decoder.resolution.name
        service.decoder.resolution.resolution = decoder.resolution.resolution
        service.decoder.energy.resolution = decoder.energy.resolution
        service.decoder.energy.energy_consumption = decoder.energy.energy_consumption
        
    """
    ################################################################################################
        
    """
        #print(f'\n\nInitial resolution: {service.decoder.resolution.resolution}')
        #print(f'\nInitial energy: {service.decoder.energy.energy_consumption}')
        resolution_set = Decoder.get_resolution_set()
        choice = random.randint(-1, 1)
        if choice!= 0:
            resolution_name = service.decoder.resolution.resolution
            position = 0
            for resolution in resolution_set:
                if resolution == resolution_name:
                    break
                position +=1

            if choice == -1:
                if position == 0: 
                    position = 1
                else:
                    position -=1
            else:
                if position == len(resolution_set) - 1:
                    position -=1
                else:
                    position +=1

            resolution_type= resolution_set[position]
            resolution = DecoderResolution(resolution_type)
            decoder = Decoder(resolution)
            service.decoder.resolution.name = decoder.resolution.name
            service.decoder.resolution.resolution = decoder.resolution.resolution
            service.decoder.energy.resolution = decoder.energy.resolution
            service.decoder.energy.energy_consumption = decoder.energy.energy_consumption
            #print(f'\n\nNew resolution: {service.decoder.resolution.resolution}')
            #rint(f'\nNew energy: {service.decoder.energy.energy_consumption}')
            #a = input('type to continue...')
    """
        

    @staticmethod
    def update_user_location(vr_users: List[VrHMD], user_ip: str, new_location: str) -> None:
        for user in vr_users:
            if user.ip == user_ip:
                user.previous_location = user.current_location
                user.current_location = new_location
                

    @staticmethod
    def update_users_location(vr_users: List[VrHMD]) -> None:
        current_users = onos.OnosController.get_hosts()
        for user in current_users['hosts']:
            VrController.update_user_location(
                vr_users=vr_users, 
                user_ip=user.ipAddresses[0], 
                new_location=user.locations[0]['elementId']
            )
        return