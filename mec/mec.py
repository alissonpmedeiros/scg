#!/user/bin/python3
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from vr import VrService
from numpy import random
from typing import List
import uuid


@dataclass
class MecResources:
    """ generates MEC GPU and CPU workloads """

    """ lam: rate or known number of occurences """
    gpu_lam: int    = 20
    cpu_lam: int    = 60


    def generate_cpu_resources(self, number_mecs: int):
        """generates cpu resources for MEC servers"""
        cpu_set = random.poisson(lam=self.cpu_lam, size=number_mecs)
        return cpu_set
        

    def include_zero_values(self, array) -> None:
        """ randomly set zero values for GPUs on MEC servers """
        array_len  = len(array)
        percentage = int(array_len / 3.33) #defines 30% of the array with zero values
        for i in range(0, percentage):
            while True:
                random_index = random.randint(0,array_len)
                if array[random_index] != 0:
                    array[random_index] = 0
                    break

        
    def generate_gpu_resources(self, number_mecs: int):
        """generates gpu resources for MEC servers"""
        gpu_set = random.poisson(lam=self.gpu_lam, size=number_mecs)
        self.include_zero_values(gpu_set)
        return gpu_set



@dataclass
class MecWorkloads:
    """ generates cpu and gpu workloads for mec servers"""

    mec_cpus: int = 0
    mec_gpus: int = 0

    def __post_init__(self):
        """post init method called right after creating MecWorkloads object"""
        pass



@dataclass_json
@dataclass
class Mec:
    """ represents a MEC server """
    id: str = field(init=False)
    
    overall_cpu:   int
    overall_gpu:   int 

    allocated_cpu: int = 0
    allocated_gpu: int = 0
    
    """ defines the cpu and gpu threshold for mec servers, which can allocate up to 20% of their computing resources """
    cpu_threshold: int = field(init=False)
    gpu_threshold: int = field(init=False)

    services_set: List[VrService] = field(default_factory=list, init=False)

    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())

        self.cpu_threshold = self.overall_cpu - int(self.overall_cpu * 0.2)
        self.gpu_threshold = self.overall_gpu - int(self.overall_gpu * 0.2)



@dataclass
class MecAgent:
    """" represents a MEC agent"""    
    id: str = field(init=False)

    @staticmethod
    def available_resources(mec_set: list,  mec_id: str, service: VrService) -> bool:
        """ checks resource availity at MEC server. """

        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        for mec in mec_set:
            if mec.id == mec_id:
                """ returns True if there is available resources after deploy a vr service """
                if quota['cpu'] + mec.allocated_cpu <= mec.cpu_threshold and quota['gpu'] + mec.allocated_gpu <= mec.gpu_threshold:
                    return True
                else:
                    return False

    @staticmethod
    def check_deployment(mec_set: list,  mec_id: str, service: VrService) -> bool:
        """ checks if a service can be deployed on mec server i on the fly """
       
        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        for mec in mec_set:
            if mec.id == mec_id:
                """ returns True if there is available resources after deploy a vr service """
                if quota['cpu'] + mec.allocated_cpu <= mec.overall_cpu and quota['gpu'] + mec.allocated_gpu <= mec.overall_gpu:
                    return True
                else:
                    return False




    @staticmethod
    def deploy_service(mec_set: list,  mec_id: str, service: VrService) -> None:
        """ deploys a vr service on mec server """
        
        for mec in mec_set:
            if mec.id == mec_id:
                mec.allocated_cpu += service.quota.resources['cpu']
                mec.allocated_gpu += service.quota.resources['gpu']
                mec.services_set.append(service)
        

    @staticmethod
    def service_migration(mec_set: list, service: VrService):
        """ migrates a service s from mec i to mec j """ 
        pass

    @staticmethod
    def reverse_offloading(mec_set: list, service: VrService):
        """ offloads a service i back to vr hmd """ 
        pass