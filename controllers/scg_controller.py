import typing 
if typing.TYPE_CHECKING: 
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 
    
from models.vr import VideoDecoder 
from models.vr import VideoDecoderResolution 

""" controller modules """
from controllers import bs_controller as bs
from controllers import vr_controller as vr
from controllers import mec_controller as mec
from controllers import json_controller as json
from controllers import onos_controller as onos
from controllers import graph_controller as graph
from controllers import config_controller  as config
from controllers import dijkstra_controller as dijkstra 

""" other modules """
from typing import Any, List
from dataclasses import dataclass, field


@dataclass
class ScgController:
    """ SCG controller representation """
    
    onos: Any = field(init=False)
    graph: 'Graph' = field(init=False)
    mec_set: List['Mec'] = field(default_factory=list, init=False)
    vr_users: List['VrHMD'] = field(default_factory=list, init=False)
    base_station_set: List['BaseStation'] = field(default_factory=list, init=False)

    def __post_init__(self):        
        print(f'*** starting sdn controller ***')
        self.onos = onos.OnosController()
        
        print(f'*** loading mecs, base stations, and vr users files ***')
        self.load_data_sets()
        
        print(f'*** initing network graph ***')
        self.graph = graph.GraphController.get_graph(self.base_station_set, self.mec_set)
        
        print(f'*** offloading vr services ***')
        self.offload_services()

    def get_average_E2E_latency(self):
        #function variables
        total_latency = 0
        total_net_latency = 0
        total_computing_latency = 0
        services_cont = 0
        
        for user in self.vr_users:
            for service_id in user.services_ids:
                service_e2e_latency = 0
               
                if any(service_id == service.id for service in user.services_set):

                    hmd_latency = vr.VrController.get_hmd_latency(
                        base_station_set=self.base_station_set,
                        vr_users=self.vr_users,
                        user_ip=user.ip,
                    )
                    service_e2e_latency = hmd_latency
                    total_computing_latency+=hmd_latency
                    total_latency += hmd_latency
                
                else: 
                    start_node = bs.BaseStationController.get_base_station(
                        self.base_station_set, user.current_location
                    )
                    
                    target_node = mec.MecController.get_service_bs(
                        self.base_station_set, self.mec_set, service_id
                    )
                    
                    network_latency, computing_latency, ete_latency = ScgController.get_E2E_latency(
                        self.mec_set, self.graph, start_node, target_node
                    )
                    
                    #print(f'service id: {service_id} |  src: {user.current_location} -> dst: {target_node.id} = E2E latency cost: {ete_latency}')
                    service_e2e_latency = ete_latency
                    
                    
                    total_net_latency += network_latency
                    total_computing_latency+=computing_latency
                    total_latency += ete_latency

                self.change_service_video_resolution(user, service_id, service_e2e_latency)
                services_cont += 1
        
        average_net_latency = round((total_net_latency / services_cont), 3)
        average_computing_latency = round((total_computing_latency / services_cont), 3)
        average_latency = round((total_latency / services_cont), 3)
        #average_energy = self.calculate_resolution_usage(average_latency)
        return average_net_latency, average_computing_latency, average_latency#, average_energy

    @staticmethod
    def get_E2E_latency(
        mec_set: List['Mec'], graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation'
    ) -> float:
        """ calculates the end-to-end latency between a vr user and the mec where the service is deployed on """
        path, ete_latency = dijkstra.DijkstraController.get_ETE_latency(
            mec_set, graph, start_node, target_node
        )
        
        target_node_mec = mec.MecController.get_mec(mec_set, target_node)      
        start_to_target_net_latency = ete_latency - (target_node_mec.computing_latency + start_node.wireless_latency)
  
        return start_to_target_net_latency, target_node_mec.computing_latency, ete_latency 

    def offload_services(self) -> None:
        count = 0
        for vr_hmd in self.vr_users:
            for service_id in vr_hmd.services_ids:
                extracted_service = vr.VrController.remove_vr_service(
                    vr_hmd, service_id
                )
                
                start_node = bs.BaseStationController.get_base_station(
                    self.base_station_set, vr_hmd.current_location
                )

                dst_mec = mec.MecController.discover_mec(
                    self.base_station_set, self.mec_set, self.graph, start_node, extracted_service,
                )

                if dst_mec is not None:
                    mec.MecController.deploy_service(dst_mec, extracted_service)
                else:
                    count+=1
                    print("\ncould not OFFLOAD the following service: {}".format(extracted_service))
        if count > 1:
            print('could not offloading {} services'.format(count))
            a = input("press any key to continue")

    def calculate_gpu_usage(self) -> float:
        total_services = len(self.vr_users)
        total_gpus = 0

        for user in self.vr_users:
            for service in user.services_set:
                total_gpus += service.quota.resources.gpu

        for mec in self.mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    total_gpus += service.quota.resources.gpu

        result = total_gpus / total_services
        #print('total services: {} | total gpus: {}'.format(total_services, total_gpus))
        #time.sleep(1)
        return result
    
    def calculate_energy_usage(self) -> float:
        #total_services = ScgController.get_vr_services_on_HMD(self.vr_users)
        total_services = 0
        total_energy = 0
        for user in self.vr_users:
            for service in user.services_set:
                total_energy += service.decoder.energy.energy_consumption
                total_services += 1
        for mec in self.mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    total_energy += service.decoder.energy.energy_consumption
                    total_services += 1
        result = total_energy / total_services
        #print('total services: {} | total energy: {}'.format(total_services, total_energy))
        #a = input("press any key to continue")
        return round(result, 2)
    
    def calculate_HMD_energy_usage(self) -> float:
        total_services = ScgController.get_vr_services_on_HMD(self.vr_users)
        total_energy = 0
        for user in self.vr_users:
            for service in user.services_set:
                total_energy += service.decoder.energy.energy_consumption
        if total_services == 0:
            return 0
        result = total_energy / total_services
        return round(result, 2)
    
    @staticmethod
    def get_vr_services_on_HMD(vr_users: List['VrHMD'] )-> int:
        count  = 0
        for user in vr_users:
            for service in user.services_set:
                count +=1
        return count
    
    def calculate_resolution_usage(self) -> None:
        k1 = 0
        k2 = 0
        k4 = 0
        k8 = 0
        
        for user in self.vr_users:
            for service in user.services_set:
                if service.decoder.resolution.resolution == '1080p':
                    k1+=1
                elif service.decoder.resolution.resolution == '1440p':
                    k2+=1
                elif service.decoder.resolution.resolution == '4k':
                    k4+=1
                elif service.decoder.resolution.resolution == '8k':
                    k8+=1
                
        for mec in self.mec_set:
            for service in mec.services_set:
                if service.is_mobile:
                    if service.decoder.resolution.resolution == '1080p':
                        k1+=1
                    elif service.decoder.resolution.resolution == '1440p':
                        k2+=1
                    elif service.decoder.resolution.resolution == '4k':
                        k4+=1
                    elif service.decoder.resolution.resolution == '8k':
                        k8+=1
        
        
        print('\n#############################################################')
        print('1k: {} | 2k: {} | 4k: {} | 8k: {}'.format(k1, k2, k4, k8))
        print('#############################################################')        
        """
        if service_e2e_latency <= 3:
            return 4.28
        elif service_e2e_latency > 3 and service_e2e_latency <= 4.5:
            return 2.12
        elif service_e2e_latency > 4.5 and service_e2e_latency <= 5.5:
            return 1.69
        else:
            return 1.63
        """
    
    def change_service_video_resolution(self, service_owner, service_id, service_e2e_latency) -> None: 
        #TODO: this method should be moved to VrController class
        #TODO: getting the service can be optimized
        service: 'VrService' = vr.VrController.get_vr_service(self.vr_users, service_owner.ip, service_id)
        if not service:
            service = mec.MecController.get_mec_service(self.mec_set, service_id)
        resolution_type = None
        #print('#################################')
        #print('service: {}'.format(service))
        #print('current resolution: {}'.format(service.decoder.resolution.resolution))
        
        if service_e2e_latency <= 3:
            resolution_type = '8k'
        elif service_e2e_latency > 3 and service_e2e_latency <= 7:
            resolution_type = '4k'
        elif service_e2e_latency > 7 and service_e2e_latency <= 8:
            resolution_type = '1440p'
        else:
            resolution_type = '1080p'
        
        resolution = VideoDecoderResolution(resolution_type)
        decoder = VideoDecoder(resolution)
        service.decoder.resolution.name = decoder.resolution.name
        service.decoder.resolution.resolution = decoder.resolution.resolution
        service.decoder.energy.resolution = decoder.energy.resolution
        service.decoder.energy.energy_consumption = decoder.energy.energy_consumption
        
        #print('new resolution: {}'.format(service.decoder.resolution.resolution))
        #print('e2e latency: {}'.format(service_e2e_latency))
        #a = input("press any key to continue")
        
        
    def load_data_sets(self) -> list: 
        """ loads the data sets of mecs, base stations, and vr users """
        
        CONFIG = config.ConfigController.get_config()
        data_dir = CONFIG['SYSTEM']['DATA_DIR']
        mec_file = CONFIG['SYSTEM']['MEC_FILE']
        bs_file = CONFIG['SYSTEM']['BS_FILE']
        users_file = CONFIG['SYSTEM']['USERS_FILE']
        overall_mecs = CONFIG['MEC_SERVERS']['OVERALL_MECS']
        services_per_user = CONFIG['SYSTEM']['SERVICE_PER_USER']
    
        mec.MecController.init_mec_servers(overall_mecs)
        self.mec_set = json.DecoderController.decoding_to_dict(data_dir, mec_file)
        
        bs.BaseStationController.init_base_stations(self.mec_set)
        vr.VrController.init_vr_users(services_per_user)
        
        self.base_station_set = json.DecoderController.decoding_to_dict(data_dir, bs_file)
        self.vr_users = json.DecoderController.decoding_to_dict(data_dir, users_file)
        