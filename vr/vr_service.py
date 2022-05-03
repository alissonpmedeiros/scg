""" dataclasses modules """
from dataclasses import dataclass, field
from unicodedata import name

from pkg_resources import ResolutionError


""" other modules """
import uuid, random
from munch import DefaultMunch



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
class DecoderEnergy:
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
        return  96
    
    def energy_1440p(self):
        return 142
    
    def energy_4k(self):
        return 417
    
    def energy_8k(self):
        return 1761    
    
    

@dataclass
class DecoderResolution:
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
class Decoder:
    """describes the resolution and energy of the decoder"""
    resolution: DecoderResolution  
    energy: DecoderEnergy = field(init=False) 
    
    def __post_init__(self):
        self.energy = DecoderEnergy(self.resolution.resolution)
        
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
    decoder: Decoder = field(init=False)

    """ cpu_only becomes an optional field"""
    cpu_only: bool = field(default=False, init=True) 
    
    """ is_mobile becomes an optional field"""
    is_mobile: bool = field(default=False, init=True) 
    
    
    
    def __post_init__(self):
        """ set up the id """
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
        
    
        resolution_type = random.choice(Decoder.get_resolution_set())
        resolution = DecoderResolution(resolution_type)
        self.decoder = Decoder(resolution)


if __name__ == "__main__":
    vr_service = VrService()
    print(vr_service.quota)
    vr_service.quota.set_quota('small')
    print(vr_service.quota)
    print(type(vr_service.quota))