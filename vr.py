from dataclasses import dataclass, field
import uuid, random

from numpy import cumproduct

class AppWorkload:
    def __init__(self):
        pass
    
class ServiceWorload:
    """ represents a VR service workload """

@dataclass
class ServiceQuota:
    """ describes the service quotas available in the system"""
    name: str
    resources: dict = field(init=False)

    def __post_init__(self):
        self.resources = self.get_quota(self.name)


    def get_quota(self, name: str):
        default = "incorrect quota"
        return getattr(self, 'quota_' + str(name), lambda: default)()

    def quota_small(self):
        quota =  { "cpu" : 1, "gpu" : 0}
        return quota

    def quota_tiny(self):
        quota =  { "cpu" : 2, "gpu" : 0}
        return quota
    
    def quota_medium(self):
        quota =  { "cpu" : 4, "gpu" : 2}
        return quota  

    def quota_large(self):
        quota = { "cpu" : 8, "gpu" : 4}
        return quota 

    def quota_xlarge(self):
        quota = { "cpu" : 10, "gpu" : 4}
        return quota


@dataclass
class VrService:
    """ represents a VR service""" 
    id: str = field(init=False)
    quota: ServiceQuota = field(init=False)
    cpu_only: bool = field(default=False, init=True) # cpu_only becomes an optional field
    #workload: ServiceWorload
    
    
    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())
    
        """ selects a random quote for each service """
        quotas_set = ['small', 'tiny', 'medium', 'large', 'xlarge']
        
        """ if cpu_only is True, then the quotas 'large' and 'xlarge' are excluded """
        if self.cpu_only:
            quota_choice = random.choice([quota for quota in quotas_set if quota not in ['medium', 'large', 'xlarge']])
            self.quota = ServiceQuota(quota_choice)
        else:
            quota_choice = random.choice(quotas_set)
            self.quota = ServiceQuota(quota_choice)
    

@dataclass
class VrApp:
    """ represents a VR application """
    def __init__(self, refresh_rate: int, workload: AppWorkload):
        self.id = str(uuid.uuid4())
        self.refresh_rate = refresh_rate
        self.workload = workload
        self.services=[]
    

@dataclass
class VrAgent:
    """ represents and VR agent"""
    @staticmethod
    def select_services(self):
        """ selects which services should be offloaded from the HMD to MEC """
        pass
    
    @staticmethod
    def request_offloading(self):
        """ requests the services offloading to SCG controller """
        pass

@dataclass
class HMD:
    """ represents a VR HMD instance """

    cpu: int = 0
    gpu: int = 0
        
