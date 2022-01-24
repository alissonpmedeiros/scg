#!/user/bin/python3

""" dataclasses modules """
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


""" munch dictionaries module """
from munch import DefaultMunch

""" np incoder module"""
from encoder import JsonEncoder

""" importing vr module """
from vr import VrService
from vr_controller import VrController

""" import base station module """
from base_station import BaseStationController

""" import graph modules """
from graph import Dijkstra

""" other modules """
from pprint import pprint
from numpy import random
from typing import List
import uuid, json, os

@dataclass
class MecResources:
    """ generates MEC GPU and CPU workloads """

    """ lam: rate or known number of occurences """
    gpu_lam: int    = 20
    cpu_lam: int    = 60


    def generate_cpu_resources(self, number_mecs: int):
        """generates cpu resources for MEC servers"""
        cpu_set = random.poisson(lam=self.cpu_lam, size=number_mecs)
        return cpu_set
        

    def include_zero_values(self, array) -> None:
        """ randomly set zero values for GPUs on MEC servers """
        array_len  = len(array)
        percentage = int(array_len / 3.33) #defines 30% of the array with zero values
        for i in range(0, percentage):
            while True:
                random_index = random.randint(0,array_len)
                if array[random_index] != 0:
                    array[random_index] = 0
                    break

        
    def generate_gpu_resources(self, number_mecs: int):
        """generates gpu resources for MEC servers"""
        gpu_set = random.poisson(lam=self.gpu_lam, size=number_mecs)
        self.include_zero_values(gpu_set)
        return gpu_set



@dataclass
class MecWorkloads:
    """ generates cpu and gpu workloads for mec servers"""

    mec_cpus: int = 0
    mec_gpus: int = 0

    def __post_init__(self):
        pass



@dataclass_json
@dataclass
class Mec:
    """ represents a MEC server """
    id: str = field(init=False)
    
    overall_cpu:   int
    overall_gpu:   int 

    allocated_cpu: int = 0
    allocated_gpu: int = 0

    computing_latency: int = field(init=False)
    
    """ defines the cpu and gpu threshold for mec servers, which can allocate up to 20% of their computing resources """
    cpu_threshold: int = field(init=False)
    gpu_threshold: int = field(init=False)

    services_set: List[VrService] = field(default_factory=list, init=False)

    def __post_init__(self):
        """ set up the id """
        self.id = str(uuid.uuid4())

        self.cpu_threshold = self.overall_cpu - int(self.overall_cpu * 0.3)
        self.gpu_threshold = self.overall_gpu - int(self.overall_gpu * 0.3)

        self.computing_latency = round(random.uniform(1, 5), 2)



@dataclass
class MecAgent:
    """" represents a MEC agent"""    
    id: str = field(init=False)

    @staticmethod
    def available_resources(mec_set: list,  mec_id: str, service: VrService) -> bool:
        """ checks resource availity at MEC server. """

        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        for mec in mec_set:
            if mec.id == mec_id:
                """ returns True if there is available resources after deploy a vr service """
                if quota['cpu'] + mec.allocated_cpu <= mec.cpu_threshold and quota['gpu'] + mec.allocated_gpu <= mec.gpu_threshold:
                    return True
                else:
                    return False

    @staticmethod
    def check_deployment(mec_set: list,  mec_id: str, service: VrService) -> bool:
        """ checks if a service can be deployed on mec server i on the fly """
       
        """ gets a quota description as a dict with the keys 'gpu' and 'cpu' """   
        quota = service.quota.resources
        
        for mec in mec_set:
            if mec.id == mec_id:
                """ returns True if there is available resources after deploy a vr service """
                if quota['cpu'] + mec.allocated_cpu <= mec.overall_cpu and quota['gpu'] + mec.allocated_gpu <= mec.overall_gpu:
                    return True
                else:
                    return False

    @staticmethod
    def deploy_service(mec_set: list,  mec_id: str, service: VrService) -> None:
        """ deploys a vr service on mec server """
        
        for mec in mec_set:
            if mec.id == mec_id:
                mec.allocated_cpu += service.quota.resources['cpu']
                mec.allocated_gpu += service.quota.resources['gpu']
                mec.services_set.append(service)
        
    @staticmethod
    def remove_service(mec_set: list, mec_id: str, service_id: str) -> VrService:
        """ removes a service from where it is deployed """
        extracted_service = None
        service_index = 0
        for mec in mec_set:
            if mec.id == mec_id:
                for service in mec.services_set:
                    if service.id == service_id:
                        break
                    service_index += 1
                extracted_service = mec.services_set.pop(service_index)
                #print("service index: {}".format(service_index))

                """ updates the allocated resources of mec """
                mec.allocated_cpu -= extracted_service.quota.resources['cpu']
                mec.allocated_gpu -= extracted_service.quota.resources['gpu']
                break
        return extracted_service

    @staticmethod
    def get_service(mec_set: list, service_id: str) -> VrService:
        """ gets a VR service """
        for mec in mec_set:
            for service in mec.services_set:
                if service.id == service_id:
                    return service

    @staticmethod
    def get_service_server_id(mec_set: list, service_id: str) -> str:
        """ gets the mec server where the service is deployed """
        for mec in mec_set:
            for service in mec.services_set:
                if service.id == service_id:
                    return mec.id

    @staticmethod
    def get_service_bs_location(base_station_set: list, mec_set: list, service_id: str) -> str:
        """ gets the base station where mec used to deploy the service is connected """
        mec_location = MecAgent.get_service_server_id(mec_set, service_id)
        for base_station in base_station_set:
            if base_station.mec_id == mec_location:
                return base_station.id

    @staticmethod
    def get_mec_bs_location(base_station_set: list, mec_id: str) -> str:
        """ gets the base station location where the mec is attached to """
        for base_station in base_station_set:
            if base_station.mec_id == mec_id:
                return base_station.id



class MecController:
    """ represents a MEC controller for MEC servers """

    @staticmethod
    def load_mec_servers() -> dict:
        files_directory =  './mec/'
        file_name_servers = 'mecs.txt'
        with open('{}{}'.format(files_directory, file_name_servers)) as json_file:
            data = json.load(json_file)
            result = DefaultMunch.fromDict(data)
            return result

    @staticmethod
    def discover_mec(base_station_set: list, mec_set: list, vr_ip: str, service: VrService) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""
        
        host_location = VrController.get_vr_user_location(vr_ip)
        
        current_base_station = BaseStationController.get_base_station(base_station_set, host_location)
        
        if MecAgent.check_deployment(mec_set=mec_set, mec_id=current_base_station.mec_id, service=service):        
            """ mec server attached to the base station where the user is connected can deploy the vr service """
            return current_base_station.mec_id
            
        else:
            """ otherwise, we need to look for nearby mec server """
            
            best_destination = ''
            shortest_latency = float('inf')
            for link in current_base_station.links:
                bs_destination = BaseStationController.get_base_station(base_station_set, link.dst.device)
                if MecAgent.check_deployment(mec_set, bs_destination.mec_id, service):
                    """ we need to take care of the network latency """
                    if link.latency < shortest_latency:
                        best_destination = bs_destination.id

            
            if best_destination != '':
                """ a nearby mec can deploy the service """
                bs_destination = BaseStationController.get_base_station(base_station_set, best_destination)
                return bs_destination.mec_id 
            else:
                """ otherwise, we should call Dijkstra algorithm for all nodes. The initial node is where the user is connected """
                shortest_latency = float('inf')
                path = []
                for base_station in base_station_set:
                    if base_station.id != current_base_station.id and MecAgent.check_deployment(mec_set, base_station.mec_id, service):
                        """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
                        aux_path, aux_shortest_latency = Dijkstra.init_algorithm(base_station_set=base_station_set, start_node=current_base_station.id, target_node=base_station.id)
                        
                        if aux_shortest_latency <= shortest_latency:
                            path = aux_path
                            shortest_latency = aux_shortest_latency
                
                """ we need to take care of the case where there is no more mec available """
                if not path:
                    return None  

                #print(" -> ".join(path))
                """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
                bs_destination =  BaseStationController.get_base_station(base_station_set, path[-1])
                return bs_destination.mec_id


    @staticmethod
    def init_services(mec_set: list, mec: Mec) -> None:
        """ creates services that will be deployed on mec server i """
        while True:
            """ checks if mec i has gpu resources """
            cpu_only = False
            if mec.overall_gpu == 0:
                cpu_only = True

            new_service = VrService(cpu_only=cpu_only)

            if MecAgent.available_resources(mec_set, mec.id, new_service):        
                MecAgent.deploy_service(mec_set, mec.id, new_service)
            else:
                break   

    @staticmethod
    def init_servers(overall_mecs: int) -> None:
        files_directory =  './mec/'
        file_name_servers = 'mecs.txt'

        if os.path.isfile('{}{}'.format(files_directory, file_name_servers)):
            return

        """ init mec servers and vr services """
        mec_set = []

        """ generates cpu and gpu resources for all mec servers """
        mec_resources = MecResources()
        cpu_set = mec_resources.generate_cpu_resources(overall_mecs)
        gpu_set = mec_resources.generate_gpu_resources(overall_mecs)
        
        for i in range(0, overall_mecs):
            """ creating mec server i """
            overall_mec_cpu = cpu_set[i]
            overall_mec_gpu = gpu_set[i]    
            new_mec = DefaultMunch.fromDict(Mec(overall_mec_cpu, overall_mec_gpu))

            """ stores mec server on scg controller's mec set """
            mec_set.append(new_mec)
        
        """ instantiating services on each mec server """
        for mec in mec_set:
            MecController.init_services(mec_set=mec_set, mec=mec)
        
        """ transforming mecs to dict """
        new_mec_set = [] 
        for mec in mec_set:
            new_mec_set.append(mec.to_dict())
        mec_set = new_mec_set

        #a = input("")    
        """ encoding json to txt file """
        JsonEncoder.encoder(mec_set, files_directory, file_name_servers)

    @staticmethod
    def get_mec(mec_set: list, mec_id: str) -> Mec:
        """ returns a MEC server """
        for mec in mec_set:
            if mec.id  == mec_id:
                return mec   

    @staticmethod
    def print_mecs(base_station_set: list, mec_set: list):
        print("\n###############  LISTING MECS ###################\n")
        for base_station in base_station_set:
            
            mec = MecController.get_mec(mec_set, base_station.mec_id)
            print("BS: {}".format(base_station.id))
            print("ID: {}".format(mec.id))
            print("CPU: {} | ALOCATED CPU: {}".format(mec.overall_cpu, mec.allocated_cpu))
            print("GPU: {} | ALLOCATED GPU: {}".format(mec.overall_gpu, mec.allocated_gpu))
            print("LATENCY: {}".format(mec.computing_latency))
            print("Services:")
            for service in mec.services_set:
                print(service.id)
            print("-------------------------------")
        print("################    END     ##################\n")