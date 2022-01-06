""" dataclasses imports """
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from munch import Munch, DefaultMunch
from typing import List
from pprint import pprint   
import uuid, json, pprint

""" np incoder class"""
from encoder import JsonEncoder

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


@dataclass_json
@dataclass
class Mec:
    """ represents a MEC server """
    id: str = field(init=False)
    mec_agent_id: str
    
    overall_cpu:   int
    overall_gpu:   int 

    allocated_cpu: int = 0
    allocated_gpu: int = 0
    
    """ defines the cpu and gpu threshold for mec servers, which can allocate up to 20% of their computing resources """
    cpu_threshold: int = field(init=False)
    gpu_threshold: int = field(init=False)

    services_set: List[VrService] = field(default_factory=list, init=False)

    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())

        self.cpu_threshold = self.overall_cpu - int(self.overall_cpu * 0.2)
        self.gpu_threshold = self.overall_gpu - int(self.overall_gpu * 0.2)


@dataclass
class MecAgent:
    """" represents an MEC agent"""    
    id: str = field(init=False)

    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())


    def available_resources(self, mec: Mec, service: VrService) -> bool:
        """ checks resource availity at MEC server. """

        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        """ returns True if there is available resources after deploy a vr service """
        if quota['cpu'] + mec.allocated_cpu <= mec.cpu_threshold and quota['gpu'] + mec.allocated_gpu <= mec.gpu_threshold:
            return True
        else:
            return False

        

    def deploy_service(self,  mec: Mec, service: VrService) -> None:
        """ deploy a vr service on mec server """
        
        mec.allocated_cpu += service.quota.resources['cpu']
        mec.allocated_gpu += service.quota.resources['gpu']
        mec.services_set.append(service)
        


    def remove_service(self, service: VrService):
        """ removes a service from a mec server """ 
        pass


@dataclass
class ScgController:
    """ SCG controller representation """
    overall_mecs: int = field(default = 100)
    mec_set: List[Mec] = field(default_factory=list, init=False)
    mec_agent_set: List[MecAgent] = field(default_factory=list, init=False)
    base_station_set: List[dict] = field(default_factory=list, init=False)
    net_controller = OnosController()
    json_encoder = JsonEncoder()
    files_directory =  './mec/'
    file_name_servers = 'mecs.txt'

    def init_servers(self) -> None:
        """ init mec servers and vr services """
        
        """ generates cpu and gpu resources for all mec servers """
        mec_resources = MecResources()
        cpu_set = mec_resources.generate_cpu_resources(self.overall_mecs)
        gpu_set = mec_resources.generate_gpu_resources(self.overall_mecs)
        
        for i in range(0, self.overall_mecs):
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
                    break

            """ stores mec server on scg controller's mec set """
            self.mec_set.append(new_mec.to_dict())
            
            """ store mec server agent on scg controller's mec agent set """
            self.mec_agent_set.append(new_mec_agent)
        
        """ encoding json to txt file """
        self.json_encoder.encoder(self.mec_set, self.files_directory)
        

    def get_servers(self) -> None:
        with open('{}{}'.format(self.files_directory, self.file_name_servers)) as json_file:
            data = json.load(json_file)
            result = DefaultMunch.fromDict(data)
            self.mec_set = result

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

    
    def build_mec_topology(self) -> None:
        """ builds MEC topology based on the network topology built by ONOS """

        """ gets network topology from onos """
        net_topology = self.net_controller.get_topology()
        i = 0
        for base_station in net_topology:
            base_station['mec_id'] = self.mec_set[i].id 
            pprint.pprint(base_station)
            print(self.mec_set[i].id)
            i+=1
            a = input("ENTER")
            self.base_station_set.append(base_station)
            
        """ merging base stations and mec servers """

 

if __name__=='__main__':
    scg = ScgController()
    scg.get_servers()
    scg.build_mec_topology()
    pprint.pprint(scg.base_station_set[0].id)
    



