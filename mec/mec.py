#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json



""" importing vr module """
from vr.vr_service import VrService


""" other modules """
from pprint import pprint
from numpy import random
from typing import List
import uuid


@dataclass
class MecResourceController:
    """ generates MEC GPU and CPU workloads """

    """ lam: rate or known number of occurences """
    gpu_lam: int    = 270
    cpu_lam: int    = 430


    def generate_cpu_resources(self, number_mecs: int):
        """generates cpu resources for MEC servers"""
        cpu_set = random.poisson(lam=self.cpu_lam, size=number_mecs)
        return cpu_set
        

    def include_zero_values(self, array) -> None:
        """ randomly set zero values for GPUs on MEC servers """
        array_len  = len(array)
        #percentage = int(array_len / 3.33) #defines 30% of the array with zero values
        servers_without_gpus = 5
        for i in range(0, servers_without_gpus):
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




@dataclass_json
@dataclass
class Mec:
    """ represents a MEC server """
    id: str = field(init=False)
    
    overall_cpu:   int
    overall_gpu:   int 

    allocated_cpu: int = 0
    allocated_gpu: int = 0

    computing_latency: int = field(init=False)
    
    """ defines the cpu and gpu threshold for mec servers, which can allocate up to 20% of their computing resources """
    cpu_threshold: int = field(init=False)
    gpu_threshold: int = field(init=False)

    services_set: List[VrService] = field(default_factory=list, init=False)

    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())

        self.cpu_threshold = self.overall_cpu - int(self.overall_cpu * 0.9)
        self.gpu_threshold = self.overall_gpu - int(self.overall_gpu * 0.9)

        self.computing_latency = round(random.uniform(1, 5), 2)



