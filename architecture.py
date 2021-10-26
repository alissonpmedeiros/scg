import uuid
from vr import VrService

class ScgController:
    def __init__(self):
        pass

    def discover_mec(self):
        # discover a nearby MEC server to either offload or migrate the service
        pass     
    
    def service_offloading(self):
        # offload the service from HMD to MEC, vice-versa 
        pass
    
    def service_migration(self):
        # migrate the service from one MEC server to another
        pass
    
    def trade_off(self):
        # provide the trade-off analysis between migration and offloading the service back to the HMD
        pass


class VrAgent:
    def __init__(self):
        pass
    
    def select_services(self):
        # select which services should be offloaded from the HMD to MEC
        pass

    def request_offloading(self):
        # request the services offloading to SCG controller
        pass

class MecAgent:
    def __init__(self):
        pass    

    def deploy_service(self):
        # service deployment and resource allocation in a MEC server.  
        pass
    
    def check_resources(self):
        # check resource availity at MEC server.
        pass

    def allocate_resources(self):
        # allocate resources for a service in MEC server.  
        pass

class Mec:
    def __init__(self, mec_agent: MecAgent):
        self.id = uuid.uuid4()
        self.cpu = 0
        self.gpu = 0
        self.mec_agent = mec_agent


    def service_price(self, service: VrService):
        #calculate the service deployment
        pass



