import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec
    from models.base_station import BaseStation
    
from models.vr import VrHMD 
from models.vr import VrService 
from models.vr import ServiceQuota

""" controller modules """
from controllers import bs_controller 
from controllers import mec_controller 
from controllers import onos_controller 
from controllers import json_controller 
from controllers import config_controller

""" other modules """
import random
from typing import Dict


class VrController:
    """ represents a Vr controller """
    
    @staticmethod
    def generate_hmd_latency():
        """generates the VrHMD latency based on the file configuration"""
        
        CONFIG = config_controller.ConfigController.get_config()
        lower_latency_threshold = CONFIG['HMDS']['LOWER_LATENCY_THRESHOLD']
        upper_latency_threshold = CONFIG['HMDS']['UPPER_LATENCY_THRESHOLD']
        computing_latency = round(random.uniform(lower_latency_threshold, upper_latency_threshold), 2)
        return computing_latency

    @staticmethod
    def init_hmds(services_per_user: int) -> None:
        """inits HMDs from ONOS API"""
        
        hmds_set = {
            "hmds_set": {}
        }
        users = onos_controller.OnosController.get_hosts()
        
        for user in users['hosts']:
            key = user.ipAddresses[0]
            hmd_mac = user.mac
            previous_location = user.locations[0].elementId
            current_location = user.locations[0].elementId            
            computing_latency = VrController.generate_hmd_latency()
            
            new_hmd: VrHMD = VrHMD(hmd_mac, previous_location, current_location, computing_latency)
        
            for i in range(0, services_per_user):
                new_service = VrService(is_mobile=True)
                new_hmd.services_set.append(new_service)
                new_hmd.services_ids.append(new_service.id)
            
            hmds_set['hmds_set'][key] = new_hmd
            
        json_controller.EncoderController.encoding_to_json(hmds_set)
        return

    @staticmethod 
    def get_vr_service(
        hmds_set: Dict[str, VrHMD], hmd_ip: str, service_id: str
    ) -> dict:
        """gets a vr service """
        
        for service in hmds_set[hmd_ip].services_set:
            if service.id == service_id:
                return service
        
        return None

    @staticmethod 
    def get_vr_service_owner(hmds_set: Dict[str, VrHMD], service: VrService) -> VrHMD:
        """gets the VrHMD that owns the service"""
        
        for id, hmd in hmds_set.items():
            for service_id in hmd.services_ids:
                if service_id == service.id:
                    return id, hmd

        return None

    @staticmethod
    def get_hmd(hmds_set: Dict[str, VrHMD], hmd_ip: str) -> VrHMD:
        """gets a VrHMD"""
                
        return hmds_set[hmd_ip]

    @staticmethod
    def remove_vr_service(hmd: VrHMD, service_id: str) -> VrService:
        """ removes a service from where it is deployed """
        
        service_index = [vr_service.id for vr_service in hmd.services_set].index(service_id)
        extracted_service = hmd.services_set.pop(service_index)
        
        return extracted_service

    @staticmethod
    def deploy_vr_service(
        hmds_set: Dict[str, VrHMD], hmd_ip: str, service: VrService
    ) -> None:
        """deployes a VrService into a VrHMD"""
        
        hmds_set[hmd_ip].services_set.append(service)
        return

    @staticmethod 
    def get_hmd_latency(base_station_set: Dict[str,'BaseStation'], vr_hmd: VrHMD) -> float:
        """ gets hmd latency, including the wireless latency where the hmd is connected to """
        
        bs_location = bs_controller.BaseStationController.get_base_station(
            base_station_set, vr_hmd.current_location
        )
        
        hmd_latency = round(bs_location.wireless_latency + vr_hmd.computing_latency, 2) 
        return hmd_latency
        
    @staticmethod
    def change_quota(service: VrService) -> None:
        """randomly changes a vr service quota """
        
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

            new_quota_name = quotas_set[position]
            service.quota.set_quota(new_quota_name)
        
        return        

    @staticmethod
    def update_hmd_position(hmds_set: Dict[str, VrHMD], hmd_ip: str, new_location: str) -> None:
        """updates the current and previous hmds location"""
        
        hmds_set[hmd_ip].previous_location = hmds_set[hmd_ip].current_location
        hmds_set[hmd_ip].current_location = new_location
        return
                
    @staticmethod
    def update_hmds_positions(hmds_set: Dict[str, VrHMD]) -> None:
        """retrives hosts from ONOS API and updates the location of hmds"""
        
        current_hosts = onos_controller.OnosController.get_hosts()
        
        for host in current_hosts['hosts']:
            hmd_ip = host.ipAddresses[0]
            hmd_location = host.locations[0]['elementId']
            
            VrController.update_hmd_position(
                hmds_set, hmd_ip, hmd_location
            )
        return
    
    def change_service_video_resolution(
        mec_set: Dict[str,'Mec'], hmds_set: Dict[str, VrHMD], service_owner_ip: str, service_id: str, service_e2e_latency: float
    ) -> None: 
        """changes the video resolution of a service based on its e2e latency"""
        
        CONFIG = config_controller.ConfigController.get_config()
        
        resolution_type = None
        
        resolution_thresholds = {
            '8k': CONFIG['SERVICES']['VIDEO_RESOLUTION']['LATENCY_THRESOLDS']['8k'],
            '4k': CONFIG['SERVICES']['VIDEO_RESOLUTION']['LATENCY_THRESOLDS']['4k'],
            '2k': CONFIG['SERVICES']['VIDEO_RESOLUTION']['LATENCY_THRESOLDS']['2k'],
        }
        
        
        if service_e2e_latency <= resolution_thresholds['8k']:
            resolution_type = '8k'
        elif service_e2e_latency <= resolution_thresholds['4k']:
            resolution_type = '4k'
        elif service_e2e_latency <= resolution_thresholds['2k']:
            resolution_type = '1440p'
        else:
            resolution_type = '1080p'
        
        service: VrService = None
        
        service = VrController.get_vr_service(hmds_set, service_owner_ip, service_id)
        
        if not service:
            service = mec_controller.MecController.get_mec_service(mec_set, service_id)
        
        service.video_decoder.set_resolution(resolution_type)
        