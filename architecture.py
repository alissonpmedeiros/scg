""" dataclasses imports """
from dataclasses import dataclass, field

""" import mec modules """
from mec.mec import MecResources, MecWorkloads, Mec, MecAgent

""" import graph modules """
from graph import Dijkstra

from munch import Munch, DefaultMunch
from typing import List
from pprint import pprint as pprint   
import uuid, json, random, time

""" np incoder class"""
from encoder import JsonEncoder

""" scg classes import """
from onos import OnosController
from vr import VrService, VrAgent



@dataclass
class ScgController:
    """ SCG controller representation """
    overall_mecs: int = field(default = 100)
    mec_set: List[Mec] = field(default_factory=list, init=False)
    base_station_set: List[dict] = field(default_factory=list, init=False)
    vr_users: List[list] = field(default_factory=list, init=False)
    files_directory =  './mec/'
    file_name_servers = 'mecs.txt'

    def __post_init__(self):
        self.get_servers()
        self.build_mec_topology()
        self.set_bs_net_latency()
        self.get_vr_users()
        self.start_mobile_vr_services()
        ''''
        '''
        
    def get_vr_users(self) -> None:
        users = OnosController.get_hosts()
        for user in users['hosts']:
            user['services'] = []
            self.vr_users.append(user)

    def start_mobile_vr_services(self):
        """ start vr services for mobile vr users """

        '''
        '''
        services_per_user = 2
        users = self.vr_users
        for user in users:
            user_ip = user.ipAddresses[0]
            for i in range(0, services_per_user):
                service = VrService()
                mec_id = self.discover_mec(user_ip, service)

                if mec_id is not None:
                    MecAgent.deploy_service(self.mec_set, mec_id, service)
                    user.services.append(service.id)
                else:
                    print("could not deploy the following service: {}".format(service))
    
    def add_services(self, mec: Mec) -> None:
        """ creating services that will be deployed on mec server i """
        while True:
            """ checks if mec i has gpu resources """
            cpu_only = False
            if mec.overall_gpu == 0:
                cpu_only = True

            new_service = VrService(cpu_only)

            if MecAgent.available_resources(self.mec_set, mec.id, new_service):        
                MecAgent.deploy_service(self.mec_set, mec.id, new_service)
            else:
                break    

    def init_servers(self) -> None:
        """ init mec servers and vr services """
        
        """ generates cpu and gpu resources for all mec servers """
        mec_resources = MecResources()
        cpu_set = mec_resources.generate_cpu_resources(self.overall_mecs)
        gpu_set = mec_resources.generate_gpu_resources(self.overall_mecs)
        
        for i in range(0, self.overall_mecs):
            """ creating mec server i """
            overall_mec_cpu = cpu_set[i]
            overall_mec_gpu = gpu_set[i]    
            new_mec = DefaultMunch.fromDict(Mec(overall_mec_cpu, overall_mec_gpu))

            """ stores mec server on scg controller's mec set """
            #self.mec_set.append(new_mec.to_dict())
            self.mec_set.append(new_mec)
        
        """ instantiating services on each mec server """
        for mec in self.mec_set:
            self.add_services(mec)
        
        """ transforming mecs to dict """
        new_mec_set = [] 
        for mec in self.mec_set:
            new_mec_set.append(mec.to_dict())
        self.mec_set = new_mec_set

        #a = input("")    
        """ encoding json to txt file """
        JsonEncoder.encoder(self.mec_set, self.files_directory)
        
    def get_servers(self) -> None:
        with open('{}{}'.format(self.files_directory, self.file_name_servers)) as json_file:
            data = json.load(json_file)
            result = DefaultMunch.fromDict(data)
            self.mec_set = result

    def get_mec(self, id: str) -> Mec:
        """ returns a MEC server """
        for mec in self.mec_set:
            if mec.id  == id:
                return mec   

    def get_base_station(self, id: str) -> dict:
        for base_station in self.base_station_set:
            if base_station.id == id:
                return base_station

    def generate_bs_latency_keys(self):
        """ creates dict keys on each base station data structure """
        for base_station in self.base_station_set:
            for link in base_station.links:
                link['latency'] = 0.0
                link['wireless_latency'] = round(random.uniform(0.1, 0.3), 2)  

    def set_destination_latency(self, src_id, dst_id, latency: float) -> None:
        """ sets the same latency of the source node on the destination node """
        for base_station in self.base_station_set:
            for link in base_station.links:
                """ 
                the test occurs in a inverse way (src with dst) because we have to make sure that only a unique link that belongs to a base station will have the same 'latency' parameter 
                """
                if link.src.device == dst_id and link.dst.device == src_id:
                    link.latency = latency
                    break
                
    def set_bs_net_latency(self):
        """ generates the network latency for base station i"""
        self.generate_bs_latency_keys()
        
        for base_station in self.base_station_set:
            """ includes the delay on each base station destination """
            for link in base_station.links:
                """ generates the network latencty randomly """
                net_latency = round(random.uniform(0.1, 1), 2)    
                link.latency = net_latency
                
                """ makes sure that A to B has the same delay of B to A"""
                self.set_destination_latency(base_station.id, link.dst.device, net_latency)

    def build_mec_topology(self) -> None:
        """ builds MEC topology based on the network topology built by ONOS """

        """ gets base stations topology from onos """
        bs_topology = OnosController.get_topology()
        total_mecs_without_gpus = int(len(bs_topology) * 0.2)
        mecs_without_gpus = 0
        i = 0

        for base_station in bs_topology:
            """ if-else statement controls how many mec servers without gpus must exist in the system (20%) """
            if self.mec_set[i].overall_gpu == 0 and mecs_without_gpus < total_mecs_without_gpus:
                mecs_without_gpus += 1
            else:
                while True:
                    i+=1
                    if self.mec_set[i].overall_gpu != 0:
                        break
            
            """ gets a mec server id and stores it on the base station object"""
            base_station['mec_id'] = self.mec_set[i].id 
            self.base_station_set.append(base_station)
            i+=1
                               
    def discover_mec(self, vr_ip: str, service: VrService) -> str:
        """ discover a nearby MEC server to either offload or migrate the service"""
        
        host = OnosController.get_host(vr_ip)
        host_location = host.locations[0].elementId
        
        current_base_station = self.get_base_station(host_location)
        

        if MecAgent.check_deployment(mec_set=self.mec_set, mec_id=current_base_station.mec_id, service=service):        
            """ mec server attached to the base station where the user is connected can deploy the vr service """
            return current_base_station.mec_id
            
        else:
            """ otherwise, we need to look for nearby mec server """
            
            best_destination = ''
            shortest_latency = float('inf')
            for link in current_base_station.links:
                bs_destination = self.get_base_station(link.dst.device)
                if MecAgent.check_deployment(self.mec_set, bs_destination.mec_id, service):
                    """ we need to take care of the network latency """
                    if link.latency < shortest_latency:
                        best_destination = bs_destination.id

            
            if best_destination != '':
                """ a nearby mec can deploy the service """
                bs_destination = self.get_base_station(best_destination)
                return bs_destination.mec_id 
            else:
                """ otherwise, we should call Dijkstra algorithm for all nodes. The initial node is where the user is connected """
                shortest_latency = float('inf')
                path = []
                for base_station in self.base_station_set:
                    if base_station.id != current_base_station.id and MecAgent.check_deployment(self.mec_set, base_station.mec_id, service):
                        """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
                        aux_path, aux_shortest_latency = Dijkstra.init_algorithm(base_station_set=self.base_station_set, start_node=current_base_station.id, target_node=base_station.id)
                        
                        if aux_shortest_latency <= shortest_latency:
                            path = aux_path
                            shortest_latency = aux_shortest_latency
                
                """ we need to take care of the case where there is no more mec available """
                if not path:
                    return None  

                #print(" -> ".join(path))
                """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
                bs_destination =  self.get_base_station(path[-1])
                return bs_destination.mec_id

    def calculate_ETE(self, src_location: str, dst_location: str):
        """ calculates the end-to-end latency between two entities """
        
        path, ete_latency = Dijkstra.init_algorithm(base_station_set=self.base_station_set, start_node=src_location, target_node=dst_location)

        #print(" -> ".join(path))
        #print("latency: {}".format(ete_latency))
        return round(ete_latency, 2)
    

    def check_migration(self):
        for user in self.vr_users:
            for service_id in user.services:
                host = OnosController.get_host(user.ipAddresses[0])
                user_location = host.locations[0].elementId
                
                service_content = MecAgent.get_service(self.mec_set, service_id)
                service_server_id = MecAgent.get_service_server_id(self.mec_set, service_id)
                service_location = MecAgent.get_service_bs_location(self.base_station_set, self.mec_set, service_id)
                previous_service_latency = self.calculate_ETE(user_location, service_location)

                mec_id_candidate = self.discover_mec(user.ipAddresses[0], service_content)
                mec_candidate_location = MecAgent.get_mec_bs_location(self.base_station_set, mec_id_candidate)
                 
                if mec_candidate_location is not None:
                    new_service_latency = self.calculate_ETE(user_location, mec_candidate_location)

                    if new_service_latency < previous_service_latency:
                        extracted_service = MecAgent.remove_service(self.mec_set,  service_server_id, service_id)
                        MecAgent.deploy_service(self.mec_set, mec_id_candidate, extracted_service)
                        print("*** Performing migration ***\n")
                        print("service {} move from MEC {} to {}\n".format(service_id, service_server_id, mec_id_candidate))
                        
                else:
                    print("**** no candidates ****")
                    """ Migration should be performed but there is no more mec available to host the service. We should consider a service migration violation... """
                    
                
               


    def trade_off(self):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""
        pass

    def print_mecs(self):
        print("\n###############  LISTING MECS ###################\n")
        for base_station in self.base_station_set:
            
            mec = self.get_mec(base_station.mec_id)
            print("BS: {}".format(base_station.id))
            print("ID: {}".format(mec.id))
            print("CPU: {} | ALOCATED CPU: {}".format(mec.overall_cpu, mec.allocated_cpu))
            print("GPU: {} | ALLOCATED GPU: {}".format(mec.overall_gpu, mec.allocated_gpu))
            print("Services:")
            for service in mec.services_set:
                print(service.id)
            print("-------------------------------")
        print("################    END     ##################\n")




def start_system() -> None:
    scg = ScgController()
    #scg.print_mecs()
    #pprint(scg.vr_users)
    #print("\n")
    #a = input("start check migration!")
    while True:
        print("\n\n##############################\n")
        scg.check_migration()
        time.sleep(1)
        
    

if __name__=='__main__':
    start_system()


    

