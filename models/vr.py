""" other modules """
import uuid, random
from typing import List
from munch import DefaultMunch
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass
class ServiceQuota:
    """ describes the service quotas available in the system"""
    name: str
    resources: dict = field(init=False)

    def __post_init__(self):
        self.resources = self.get_quota(self.name)

    def set_quota(self, name: str):
        self.name = name
        self.resources = self.get_quota(name)

    def get_quota(self, name: str):
        default = "incorrect quota"
        return getattr(self, 'quota_' + str(name), lambda: default)()

    def quota_small(self):
        quota =  { "cpu" : 1, "gpu" : 0}
        return DefaultMunch.fromDict(quota)

    def quota_tiny(self):
        quota =  { "cpu" : 2, "gpu" : 1}
        return DefaultMunch.fromDict(quota)
    
    def quota_medium(self):
        quota =  { "cpu" : 2, "gpu" : 2}
        return DefaultMunch.fromDict(quota)  

    def quota_large(self):
        quota = { "cpu" : 4, "gpu" : 2}
        return DefaultMunch.fromDict(quota) 

    def quota_xlarge(self):
        quota = { "cpu" : 4, "gpu" : 4}
        return DefaultMunch.fromDict(quota)
    
    @staticmethod
    def get_quotas_set():
        quotas_set = ['small', 'tiny', 'medium', 'large', 'xlarge']
        return quotas_set


@dataclass
class VideoDecoderEnergy:
    """ describes the energy consumption of the decoder """
    resolution: str
    energy_consumption: str = field(init=False)
    
    def __post_init__(self):
        self.energy_consumption = self.get_energy(self.resolution)
    
    def set_energy(self, resolution: str):
        self.resolution = resolution
        self.energy_consumption = self.get_energy(resolution)
    
    def get_energy(self, resolution: str):
        default = "incorrect energy"
        return getattr(self, 'energy_' + str(resolution), lambda: default)()

    def energy_1080p(self):
        return  1.63
    
    def energy_1440p(self):
        return 1.69
    
    def energy_4k(self):
        return 2.12
    
    def energy_8k(self):
        return 4.28    
    
    

@dataclass
class VideoDecoderResolution:
    """describes the resolution of the decoder"""
    name: str
    resolution: str = field(init=False)
    
    def __post_init__(self):
        self.resolution = self.get_resolution(self.name) 
    
    def set_resolution(self, name: str):
        self.name = name
        self.resolution = self.get_resolution(name)
    
    def get_resolution(self, name: str):
        default = "incorrect resolution"
        return getattr(self, 'resolution_' + str(name), lambda: default)()
    
    def resolution_8k(self):
        return "8k"
    
    def resolution_4k(self):
        return "4k"
    
    def resolution_1440p(self):
        return "1440p"
    
    def resolution_1080p(self):
        return "1080p"
    

@dataclass
class VideoDecoder:
    """describes the resolution and energy of the decoder"""
    resolution: VideoDecoderResolution  
    energy: VideoDecoderEnergy = field(init=False) 
    
    def __post_init__(self):
        self.energy = VideoDecoderEnergy(self.resolution.resolution)
        
    def get_energy(self):
        return self.energy
    
    def get_resolution(self):
        return self.resolution
        
    def get_resolution_set():
        resolution_set = ['1080p', '1440p', '4k', '8k']
        return resolution_set

@dataclass
class VrService:
    """ represents a VR service""" 
    id: str = field(init=False)
    quota: ServiceQuota = field(init=False)
    decoder: VideoDecoder = field(init=False)
    cpu_only: bool = field(default=False, init=True) 
    is_mobile: bool = field(default=False, init=True) 
    
    def __post_init__(self):
        self.id = str(uuid.uuid4())
        quotas_set = ServiceQuota.get_quotas_set()
        
        """ if cpu_only is True, then the quotas 'large' and 'xlarge' are excluded """
        if self.cpu_only:
            """ selects a random quote for each service """
            quota_choice = random.choice([
                quota for quota in quotas_set if quota not in ['medium', 'large', 'xlarge']])
            self.quota = ServiceQuota(quota_choice)
        else:
            quota_choice = random.choice(quotas_set)
            self.quota = ServiceQuota(quota_choice)
        
        resolution_type = random.choice(VideoDecoder.get_resolution_set())
        resolution = VideoDecoderResolution(resolution_type)
        self.decoder = VideoDecoder(resolution)



@dataclass_json
@dataclass
class VrHMD:
    """ represents a VR HMD instance """
    
    ip: str
    mac_address: str
    previous_location: str 
    current_location:  str 
    computing_latency: float 
    cpu: int = 0
    gpu: int = 0
    id: str = field(init=False)
    services_set: List[VrService] = field(default_factory=list, init=False)
    services_ids: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.id = str(uuid.uuid4())

        
    