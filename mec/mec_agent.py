""" dataclasses modules """
from typing import List
from mec.mec import Mec
from dataclasses import dataclass, field
from base_station.bs_controller import BaseStation
from vr.vr_service import VrService


@dataclass
class MecAgent:
    """" represents a MEC agent"""    
    id: str = field(init=False)

    @staticmethod
    def available_resources(
        mec_set: List[Mec],  
        mec_id: str, 
        service: VrService
    ) -> bool:
        """ checks resource availity at MEC server. """

        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        for mec in mec_set:
            if mec.id == mec_id:
                """ returns True if there is available resources after deploy a vr service """
                if quota.cpu + mec.allocated_cpu <= mec.cpu_threshold and quota.gpu + mec.allocated_gpu <= mec.gpu_threshold:
                    return True
                else:
                    return False

    @staticmethod
    def check_deployment(
        mec_set: List[Mec],  
        mec_id: str, 
        service: VrService
    ) -> bool:
        """ checks if a service can be deployed on mec server i on the fly """
       
        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        for mec in mec_set:
            if mec.id == mec_id:
                """ returns True if there is available resources after deploy a vr service """
                if quota.cpu + mec.allocated_cpu <= mec.overall_cpu and quota.gpu + mec.allocated_gpu <= mec.overall_gpu:
                    return True
                else:
                    return False

    @staticmethod
    def deploy_service(mec_set: List[Mec],  mec_id: str, service: VrService) -> None:
        """ deploys a vr service on mec server """
        
        for mec in mec_set:
            if mec.id == mec_id:
                mec.allocated_cpu += service.quota.resources.cpu
                mec.allocated_gpu += service.quota.resources.gpu
                mec.services_set.append(service)
        
    @staticmethod
    def remove_service(
        mec_set: List[Mec], 
        mec_id: str, 
        service_id: str) -> VrService:
        """ removes a service from where it is deployed """
        extracted_service = None
        service_index = 0
        for mec in mec_set:
            if mec.id == mec_id:
                for service in mec.services_set:
                    if service.id == service_id:
                        break
                    service_index += 1
                extracted_service = mec.services_set.pop(service_index)
                #print("service index: {}".format(service_index))

                """ updates the allocated resources of mec """
                mec.allocated_cpu -= extracted_service.quota.resources.cpu
                mec.allocated_gpu -= extracted_service.quota.resources.gpu
                break
        return extracted_service

    @staticmethod
    def get_mec_service(mec_set: List[Mec], service_id: str) -> VrService:
        """ gets a VR service that is deployed on mec server """
        for mec in mec_set:
            for service in mec.services_set:
                if service.id == service_id:
                    return service

    @staticmethod
    def get_service_server_id(mec_set: List[Mec], service_id: str) -> str:
        """ gets the mec server where the service is deployed """
        for mec in mec_set:
            for service in mec.services_set:
                if service.id == service_id:
                    return mec.id
        return None

    @staticmethod
    def get_service_bs_id(
        base_station_set: List[BaseStation], mec_set: List[Mec], service_id: str
    ) -> str:
        """ gets the base station where the mec (used to deploy the service) is attached to """
        service_server_id = MecAgent.get_service_server_id(mec_set, service_id)
        for base_station in base_station_set:
            if base_station.mec_id == service_server_id:
                return base_station.id

    @staticmethod
    def get_mec_bs_location(base_station_set: List[BaseStation], mec_id: str) -> str:
        """ gets the base station location where the mec is attached to """
        for base_station in base_station_set:
            if base_station.mec_id == mec_id:
                return base_station.id

