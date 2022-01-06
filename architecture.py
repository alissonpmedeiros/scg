from dataclasses import dataclass, field
from typing import List
from numpy.random.mtrand import random

from pprint import pprint   
import uuid, random

""" scg classes import """
from onos import OnosController
from mec.mec import MecResources, MecWorkloads
from vr import VrService


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
class Mec:
    """ represents a MEC server """
    mec_agent_id: uuid.UUID
    
    overall_cpu:   int
    overall_gpu:   int 

    allocated_cpu: int = 0
    allocated_gpu: int = 0
    
    services_set: List[VrService] = field(default_factory=list, init=False)
    
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    
    """ defines the cpu and gpu threshold for mec servers, which can allocate up to 20% of their computing resources """
    cpu_threshold: int = field(init=False)
    gpu_threshold: int = field(init=False)

    def __post_init__(self):
        self.cpu_threshold = self.overall_cpu - int(self.overall_cpu * 0.2)
        self.gpu_threshold = self.overall_gpu - int(self.overall_gpu * 0.2)


@dataclass
class MecAgent:
    """" represents an MEC agent"""    
    id: uuid.UUID = field(default_factory=uuid.uuid4)


    def available_resources(self, mec: Mec, service: VrService) -> bool:
        """ checks resource availity at MEC server. """

        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.quota_description
        
        """ returns True if there is available resources after deploy a vr service """
        if quota['cpu'] + mec.allocated_cpu <= mec.cpu_threshold and quota['gpu'] + mec.allocated_gpu <= mec.gpu_threshold:
            return True
        else:
            return False

        

    def deploy_service(self,  mec: Mec, service: VrService) -> None:
        """ deploy a vr service on mec server """
        
        mec.allocated_cpu += service.quota.quota_description['cpu']
        mec.allocated_gpu += service.quota.quota_description['gpu']
        mec.services_set.append(service)
        


    def remove_service(self, service: VrService):
        """ removes a service from a mec server """ 
        pass


@dataclass
class ScgController:
    """ SCG controller representation """
    
    mec_set: List[Mec] = field(default_factory=list, init=False)
    mec_agent_set: List[MecAgent] = field(default_factory=list, init=False)
    net_controller = OnosController()


    def print_mec(self, mec: Mec):
        print("\nID: {} \nCPUS: {} | ALLOCATED CPUs {} \nGPUS: {} | ALLOCATED GPUs {} \nMEC AGENT: {} \nSERVICES:".format(mec.id, mec.overall_cpu, mec.allocated_cpu, mec.overall_gpu, mec.allocated_gpu, mec.mec_agent_id))
        pprint(mec.services_set)
        print("\n")

    def print_mecs(self):
        for mec in self.mec_set:
            print("ID: {} \nCPUS: {} | ALLOCATED CPUs {} \nGPUS: {} | ALLOCATED GPUs {} \nMEC AGENT: {} \nSERVICES:".
            format(mec.id, mec.overall_cpu, mec.allocated_cpu, mec.overall_gpu, mec.allocated_gpu, mec.mec_agent_id))
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
            """ creating mec agent i """
            new_mec_agent = MecAgent()

            """ creating mec server i """
            new_mec_cpu = cpu_set[i]
            new_mec_gpu = gpu_set[i]    
            new_mec = Mec(new_mec_agent.id, new_mec_cpu, new_mec_gpu)

            """ creating services that will be deployed on mec server i """
            while True:
                """ checks if mec i has gpu resources """
                cpu_only = False
                if new_mec.overall_gpu == 0:
                    cpu_only = True

                new_service = VrService(cpu_only)

                if new_mec_agent.available_resources(new_mec, new_service):        
                    new_mec_agent.deploy_service(new_mec, new_service)
                else:
                    self.print_mec(new_mec)
                    a = input("WHILE BREAK!")
                    break



            """ stores mec server on scg controller's mec set """
            self.mec_set.append(new_mec)

            """ store mec server agent on scg controller's mec agent set """
            self.mec_agent_set.append(new_mec_agent)

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
    
    



