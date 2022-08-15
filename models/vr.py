""" other modules """
import uuid, random
from typing import List
from munch import DefaultMunch
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ServiceQuota:
    """ describes the service quotas available in the system"""
    
    name: str = field(default_factory=str, init=True)
    resources: dict = field(default_factory=dict, init=True)

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
    
    
@dataclass_json
@dataclass
class VideoDecoderEnergy:
    """ describes the energy consumption of the decoder """
    
    energy_consumption: str = field(default_factory=str, init=True)
    
    def set_energy(self, resolution_name: str):
        self.energy_consumption = self.get_energy(resolution_name)
    
    def get_energy(self, resolution_name: str):
        default = "incorrect energy"
        return getattr(self, 'energy_' + str(resolution_name), lambda: default)()

    def energy_1080p(self):
        return  1.63
    
    def energy_1440p(self):
        return 1.69
    
    def energy_4k(self):
        return 2.12
    
    def energy_8k(self):
        return 4.28    
    
    
@dataclass_json
@dataclass
class VideoDecoderResolution:
    """describes the resolution of the decoder"""
    
    resolution: str = field(default_factory=str, init=True)
    
    def set_resolution(self, resolution_name: str):
        self.resolution = self.get_resolution(resolution_name)
    
    def get_resolution(self, resolution_name: str):
        default = "incorrect resolution"
        return getattr(self, 'resolution_' + str(resolution_name), lambda: default)()
    
    def resolution_8k(self):
        return "8k"
    
    def resolution_4k(self):
        return "4k"
    
    def resolution_1440p(self):
        return "1440p"
    
    def resolution_1080p(self):
        return "1080p"
    
@dataclass_json
@dataclass
class VideoDecoder:
    """describes the resolution and energy of the decoder"""
    resolution: VideoDecoderResolution = field(default_factory=VideoDecoderResolution, init=True)
    energy: VideoDecoderEnergy = field(default_factory=VideoDecoderEnergy, init=True) 
    
    def __post_init__(self):
        if not self.resolution:
            self.resolution = VideoDecoderResolution()
            self.energy = VideoDecoderEnergy()
    
    @staticmethod    
    def get_resolution_set():
        resolution_set = ['1080p', '1440p', '4k', '8k']
        return resolution_set
    
    def set_resolution(self, resolution_name: str):
        self.resolution.set_resolution(resolution_name)
        self.energy.set_energy(resolution_name)

@dataclass_json
@dataclass
class VrService:
    """ represents a VR service""" 
    id: str = field(default_factory=str, init=True)
    quota: ServiceQuota = field(default_factory=ServiceQuota, init=True)
    video_decoder: VideoDecoder = field(default_factory=VideoDecoder, init=True)
    cpu_only: bool = field(default=False, init=True) 
    is_mobile: bool = field(default=False, init=True) 
    
    
    def __post_init__(self):
        if not self.id:
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
            
            self.video_decoder = VideoDecoder()
            resolution_name = random.choice(VideoDecoder.get_resolution_set())        
            self.video_decoder.set_resolution(resolution_name)

      
@dataclass_json
@dataclass
class VrHMD:
    """ represents a VR HMD instance """
    
    mac_address: str
    previous_location: str 
    current_location:  str 
    computing_latency: float 
    cpu: int = 0
    gpu: int = 0
    services_set: List[VrService] = field(default_factory=list, init=True)
    services_ids: List[str] = field(default_factory=list, init=True)
