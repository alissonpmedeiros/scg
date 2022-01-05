from dataclasses import dataclass, field
import uuid, random

class AppWorkload:
    def __init__(self):
        pass
    
class ServiceWorload:
    """ represents a VR service workload """

@dataclass
class ServiceQuota:
    """ describes the service quotas available in the system"""
    quota_name: str
    quota: dict = field(init=False)

    def __post_init__(self):
        self.quota = self.get_quota(self.quota_name)


    def get_quota(self, quota_name: str):
        default = "incorrect quota"
        return getattr(self, 'quota_' + str(quota_name), lambda: default)()

    def quota_tiny(self):
        quota =  { "cpu" : 2, "gpu" : 0}
        return quota
    
    def quota_medium(self):
        quota =  { "cpu" : 2, "gpu" : 1}
        return quota  

    def quota_large(self):
        quota = { "cpu" : 4, "gpu" : 2}
        return quota 

    def quota_xlarge(self):
        quota = { "cpu" : 8, "gpu" : 4}
        return quota


@dataclass
class VrService:
    """ represents a VR service""" 
    quota: ServiceQuota = field(init=False)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    #workload: ServiceWorload
    
    
    def __post_init__(self):
        """ selects a random quote for each service """
        quotas_set = ['tiny', 'medium', 'large', 'xlarge']
        quota_choice = random.choice(quotas_set)
        self.quota = ServiceQuota(quota_choice)
    

@dataclass
class VrApp:
    """ represents a VR application """
    def __init__(self, refresh_rate: int, workload: AppWorkload):
        self.id = uuid.uuid4()
        self.refresh_rate = refresh_rate
        self.workload = workload
        self.services=[]
    


@dataclass
class HMD:
    """ represents a VR HMD instance """

    cpu: int = 0
    gpu: int = 0
        
