"""model modules"""
from models.vr import VrService

""" other modules """
from typing import List
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Mec:
    """ represents a MEC server """
    
    name: str
    overall_cpu: int
    overall_gpu: int 
    computing_latency: float 
    init_resource_load: float
    allocated_cpu: int = 0
    allocated_gpu: int = 0
    
    """ defines the cpu and gpu threshold for mec servers, which can allocate up to 20% of their computing resources """
    cpu_threshold: int = field(default_factory=int, init=True)
    gpu_threshold: int = field(default_factory=int, init=True)

    services_set: List[VrService] = field(default_factory=list, init=True)

    def __post_init__(self):
        self.cpu_threshold = self.overall_cpu - int(self.overall_cpu * self.init_resource_load)
        self.gpu_threshold = self.overall_gpu - int(self.overall_gpu * self.init_resource_load)



