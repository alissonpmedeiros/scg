from dataclasses import dataclass
import uuid

class AppWorkload:
    def __init__(self):
        pass
    
class ServiceWorload:
    """ represents a VR service workload """

@dataclass(frozen=True)
class ServiceQuota:
    """ describes the service quotas available in the system"""

    def get_quota(self, quota_name: str):
        default = "incorrect quota"
        return getattr(self, 'quota_' + str(quota_name), lambda: default)()

    def quota_tiny(self):
        quota =  { "cpu" : 1, "gpu" : 0}
        return quota
    
    def quota_medium(self):
        quota =  { "cpu" : 2, "gpu" : 0}
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
    quota: ServiceQuota
    workload: ServiceWorload
    id: uuid.UUID = uuid.uuid4()
    


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
        





