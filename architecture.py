from dataclasses import dataclass, field
from typing import List
import uuid

from numpy.random.mtrand import random
from vr import VrService
from mec.mec import MecResources, MecWorkloads
from onos import OnosController
import time, random
from pprint import pprint   
    
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
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def check_resources(self):
        """ check resource availity at MEC server. """
        pass

    def allocate_resources(self):
        """ allocate resources for a service in MEC server. """ 
        pass



@dataclass
class Mec:
    """ represents a MEC server """
    
    overall_cpu:   int
    available_cpu: int = field(init=False)
    
    overall_gpu:    int 
    available_gpu: int = field(init=False)
    
    mec_agent: MecAgent
    #services_set = List[VrService]
    services_set: List[VrService] = field(default_factory=list, init=False)
    
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    

    def __post_init__(self):
        """ init available cpu and gpu with overall cpu and gpu rspectively """
        self.available_cpu = self.overall_cpu
        self.available_gpu = self.overall_gpu
       

    def add_service(self, service: VrService) -> None:
        self.services_set.append(service)
        
    '''
    def remove_service(self, id: uuid.UUID):
        for i in range(len(self.services_set)):
             if self.services_set[i]==id:
                 del self.services_set[i]
                 break
    '''





@dataclass
class ScgController:
    """ SCG controller representation """
    
    mec_set = []
    net_controller = OnosController()


    def print_mecs(self):
        for mec in self.mec_set:
            print("ID: {} \nCPUS: {} | AVAILABLE CPUs {} \nGPUS: {} | AVAILABLE GPUs {} \nSERVICES:".
            format(mec.id, mec.overall_cpu, mec.available_cpu, mec.overall_gpu, mec.available_gpu))
            pprint(mec.services_set)
            print("\n")

    def init_servers(self):
        """ init mec servers and vr services """
        overall_mecs = 5
        
        """ generates cpu and gpu resources for all mec servers """
        mec_resources = MecResources()
        cpu_set = mec_resources.generate_cpu_resources(overall_mecs)
        gpu_set = mec_resources.generate_gpu_resources(overall_mecs)
        
        for i in range(0, overall_mecs):
            """ creating mec server i """
            new_mec_cpu = cpu_set[i]
            new_mec_gpu = gpu_set[i]    
            new_mec_agent = MecAgent()
            new_mec = Mec(new_mec_cpu, new_mec_gpu, new_mec_agent)

            """ creating services that will be deployed on mec server i """
            average_services = 3
            overall_services =  random.randint(1, average_services)
            #print("overall services: {}".format(overall_services))
            for i in range(0, overall_services):
                new_service = VrService()
                new_mec.add_service(new_service)

            
            """ store mec server on scg controller's mec set """
            self.mec_set.append(new_mec)
            #pprint(self.mec_set)

            #print("\n")
            #pprint(new_mec.services_set)
            #a = input("ENTER:")
        self.print_mecs()

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
        

        '''
        f = open("{}cpu_resources.txt".format(self.files_directory), "w+")
        for i in cpu_set:
            f.write("{} \n".format(i))
        f.close()
        '''

        net_topology = self.net_controller.get_topology()
        for node in net_topology:
            print(node)
 

if __name__=='__main__':
    scg = ScgController()
    scg.init_servers()
    
    