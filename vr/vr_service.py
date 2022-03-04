""" dataclasses modules """
from dataclasses import dataclass, field


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

    """ cpu_only becomes an optional field"""
    cpu_only: bool = field(default=False, init=True) 
    
    """ is_mobile becomes an optional field"""
    is_mobile: bool = field(default=False, init=True) 
    
    
    
    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())
    
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
        
    



