from dataclasses import dataclass, field
from typing import List
import uuid
from numpy import true_divide

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
class Mec:
    """ represents a MEC server """
    mec_agent_id: uuid.UUID
    
    overall_cpu:   int
    overall_gpu:   int 

    allocated_cpu: int = 0
    allocated_gpu: int = 0
    
    services_set: List[VrService] = field(default_factory=list, init=False)
    
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    
       

        
    '''
    def remove_service(self, id: uuid.UUID):
        for i in range(len(self.services_set)):
             if self.services_set[i]==id:
                 del self.services_set[i]
                 break
    '''


@dataclass
class MecAgent:
    """" represents an MEC agent"""    
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def available_resources(self, mec: Mec, service: VrService) -> bool:
        """ check resource availity at MEC server. """

        cpu_threshold = mec.overall_cpu - int(mec.overall_cpu * 0.2)
        gpu_threshold = mec.overall_gpu - int(mec.overall_gpu * 0.2)


        """ gets a quota description represented as a dict """   
        quota = service.quota.quota_description
        
        """ returns True if there is available resources right after deploy a vr service  """
        print('cpu quota + allocated [{}] <= [{}]'.format(quota['cpu'] + mec.allocated_cpu, cpu_threshold))

        print('gpu quota + allocate [{}] <= [{}]:'.format(quota['gpu'] + mec.allocated_gpu, gpu_threshold))

        
        if quota['cpu'] + mec.allocated_cpu <= cpu_threshold and quota['gpu'] + mec.allocated_gpu <= gpu_threshold:
            return True
        else:
            return False

        

    def deploy_service(self,  mec: Mec, service: VrService) -> bool:
        """ deploy a vr service on mec server """
        
        if self.available_resources(mec, service):
            mec.allocated_cpu += service.quota.quota_description['cpu']
            mec.allocated_gpu += service.quota.quota_description['gpu']
            mec.services_set.append(service) 
            return True   
        else:
            return False
        


    def allocate_resources(self):
        """ allocate resources for a service in MEC server. """ 
        pass


@dataclass
class ScgController:
    """ SCG controller representation """
    
    mec_set: List[Mec] = field(default_factory=list, init=False)
    mec_agent_set: List[MecAgent] = field(default_factory=list, init=False)
    net_controller = OnosController()


    def print_mec(self, mec: Mec):
        print("ID: {} \nCPUS: {} | ALLOCATED CPUs {} \nGPUS: {} | ALLOCATED GPUs {} \nMEC AGENT: {} \nSERVICES:".format(mec.id, mec.overall_cpu, mec.allocated_cpu, mec.overall_gpu, mec.allocated_gpu, mec.mec_agent_id))
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
            average_services = 35
            overall_services =  random.randint(1, average_services)
            for i in range(0, overall_services):
                """ checks if mec i has gpu resources """
                cpu_only = False
                if new_mec.overall_gpu == 0:
                    cpu_only = True

                new_service = VrService(cpu_only)
                
                """ checks if service j can be deployed on mec i """
                if new_mec_agent.deploy_service(new_mec, new_service):
                    print('sucessfuly service deployment')
                else:
                    print('there is no available resources at mec to deploy service')
                    print('MEC: {} \nSERVICE: {}'.format(new_mec, new_service))
                
                print("\n")
                self.print_mec(new_mec)
                a = input("")        
            a = input("STOP")
            
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
    
    



