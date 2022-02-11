""" dataclasses modules """
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


""" other modules """
from typing import List
import uuid, random
from munch import DefaultMunch

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

    def set_quota(self, new_quota: str):
        self.resources = self.get_quota(new_quota)

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


@dataclass
class VrService:
    """ represents a VR service""" 
    id: str = field(init=False)
    quota: ServiceQuota = field(init=False)
    
    """ number of iterations that will be required to service change its workload"""
    iterations:int = field(init=False)   
    
    """ controls the iterations"""
    iterations_count:int = field(default=0)

    """ cpu_only becomes an optional field"""
    cpu_only: bool = field(default=False, init=True) 
    
    """ is_mobile becomes an optional field"""
    is_mobile: bool = field(default=False, init=True) 
    
    
    
    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())

        self.iterations = random.randint(20, 100)
    
        quotas_set = ['small', 'tiny', 'medium', 'large', 'xlarge']
        
        """ if cpu_only is True, then the quotas 'large' and 'xlarge' are excluded """
        if self.cpu_only:
            """ selects a random quote for each service """
            quota_choice = random.choice([
                quota for quota in quotas_set if quota not in ['medium', 'large', 'xlarge']])
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

@dataclass_json
@dataclass
class HMD:
    """ represents a VR HMD instance """
    ip: str
    mac_address: str
    cpu: int = 0
    gpu: int = 0
    id: str = field(init=False)
    computing_latency: int = field(init=False)
    services_set: List[VrService] = field(default_factory=list, init=False)
    services_ids: List[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.id = str(uuid.uuid4())
        self.computing_latency = round(random.uniform(2, 6), 2)


