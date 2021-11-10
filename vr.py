import uuid

class AppWorkload:
    def __init__(self):
        pass
    
class ServiceWorload:
    def __init__(self):
        pass


class ServiceQuota:

    def get_quota(self, quota_name: str):
        default = "incorrect quota"
        return getattr(self, 'quota_' + str(quota_name), lambda: default)()

    # VCPUs, VGPUs, Disk (in GB), RAM (in MB)

    def quota_tiny(self):
        quota =  { "cpu" : 1, "gpu" : 0, "disk"	:1 	, "ram": 512  , "price": 5 }
        return quota
    
    def quota_medium(self):
        quota =  { "cpu" : 1, "gpu" : 0, "disk"	:20 , "ram": 2048 , "price": 10}
        return quota  

    def quota_large(self):
        quota = { "cpu" : 4, "gpu" : 1, "disk"	:80 , "ram": 8192 , "price": 50}
        return quota 

    def quota_xlarge(self):
        quota = { "cpu" : 8, "gpu" : 2, "disk"	:160, "ram": 16384, "price": 80}
        return quota

class VrService:
    def __init__(self, quota: ServiceQuota):
        self.quota = quota

class VrApp:
    def __init__(self, refresh_rate: int, workload: AppWorkload):
        self.id = uuid.uuid4()
        self.refresh_rate = refresh_rate
        self.workload = workload
        self.services=[]
    
    def add_service(self, service: VrService):
        # add a service to the VR app
        pass


class HMD:
    def __init__(self):
        self.cpu = 0
        self.gpu = 0
        





