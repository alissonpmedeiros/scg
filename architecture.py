from dataclasses import dataclass
import uuid
from vr import VrService
from mec import MecResources, MecWorkloads
from onos import OnosController
import pprint, time

@dataclass
class ScgController:
    """ SCG controller representation """
    
    net_controller = OnosController()


    def discover_mec(self):
        """ discover a nearby MEC server to either offload or migrate the service"""
        pass     
    
    def service_offloading(self):
        """ offload the service from HMD to MEC, vice-versa """
        pass
    
    def service_migration(self):
        """ migrate the service from one MEC server to another"""
        pass
    
    def trade_off(self):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""
        pass    

    def build_mec_topology(self) -> dict:
        """ builds MEC topology based on the network topology built by ONOS """
        
        net_topology = self.net_controller.get_topology()
        for node in net_topology:
            print(node)

    
    
@dataclass
class VrAgent:
    """ represents and VR agent"""

    
    def select_services(self):
        """ select which services should be offloaded from the HMD to MEC """
        pass

    def request_offloading(self):
        """ request the services offloading to SCG controller """
        pass


@dataclass
class MecAgent:
    """" represents an MEC agent"""    

    def deploy_service(self):
        """service deployment and resource allocation in a MEC server.  """
        pass
    
    def check_resources(self):
        """ check resource availity at MEC server. """
        pass

    def allocate_resources(self):
        """ allocate resources for a service in MEC server. """ 
        pass



@dataclass
class Mec:
    """ represents a MEC server """
    
    mec_agent: MecAgent
    id: uuid.UUID = uuid.uuid4()
    cpu: int = 0
    gpu: int = 0
    #services: list = []


    def add_service(self, service: VrService):
        self.services.append(service)
        pass

    def remove_service(self, id: uuid.UUID):
        for i in range(len(self.services)):
             if self.services[i]==id:
                 del self.services[i]
                 break



if __name__=='__main__':
    #scg = ScgController()
    #scg.build_mec_topology()
    pass
    