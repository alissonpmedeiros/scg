import typing 
if typing.TYPE_CHECKING: 
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.base_station import BaseStation 
    

""" controller modules """
from controllers import bs_controller
from controllers import vr_controller
from controllers import mec_controller
from controllers import json_controller
from controllers import onos_controller
from controllers import graph_controller
from controllers import config_controller
from controllers import dijkstra_controller

""" other modules """
from typing import Any, Dict
from dataclasses import dataclass, field


@dataclass
class ScgController:
    """ SCG controller representation """
    
    onos: Any = field(init=False)
    graph: 'Graph' = field(init=False)
    mec_set: Dict[str,'Mec'] = field(default_factory=dict, init=False)
    hmds_set: Dict[str,'VrHMD'] = field(default_factory=dict, init=False)
    base_station_set: Dict[str,'BaseStation'] = field(default_factory=dict, init=False)

    def __post_init__(self):        
        print(f'\n*** starting sdn controller ***')
        self.onos = onos_controller.OnosController()
        
        print(f'\n*** loading mecs, base stations, and vr users files ***')
        self.load_data_sets()
        
        print(f'\n*** initing network graph ***')
        self.graph = graph_controller.GraphController.get_graph(
            self.base_station_set, self.mec_set
        )
        
        print(f'\n*** offloading vr services ***')
        self.offload_services()

    @staticmethod
    def get_E2E_latency(
        mec_set: Dict[str,'Mec'], graph: 'Graph', start_node: 'BaseStation', target_node: 'BaseStation'
    ) -> dict:
        """ calculates the end-to-end latency between a vr user and the mec where the service is deployed on """
        
        path, ete_latency = dijkstra_controller.DijkstraController.get_ETE_latency(
            mec_set, graph, start_node, target_node
        )
        
        target_node_mec = mec_controller.MecController.get_mec(mec_set, target_node)      
        net_latency = ete_latency - (target_node_mec.computing_latency + start_node.wireless_latency)

        result = {
            "network_latency": round(net_latency, 2),
            "destination_latency": round(target_node_mec.computing_latency, 2),
            "e2e_latency": round(ete_latency, 2)
        }
  
        return result

    def get_average_E2E_latency(self):
        """gets the average E2E latency of all services"""
        
        services_cont = 0
        total_net_latency = 0
        total_e2e_latency = 0
        total_computing_latency = 0
        
        for id, hmd in self.hmds_set.items():
            for service_id in hmd.services_ids: 
                if any(service_id == service.id for service in hmd.services_set):

                    hmd_latency = vr_controller.VrController.get_hmd_latency(
                        self.base_station_set, hmd
                    )
                
                    total_computing_latency += hmd_latency
                    total_e2e_latency += hmd_latency
                
                else: 
                    start_node = bs_controller.BaseStationController.get_base_station(
                        self.base_station_set, hmd.current_location
                    )
                    
                    target_node = mec_controller.MecController.get_service_bs(
                        self.base_station_set, self.mec_set, service_id
                    )
                    
                    latency = ScgController.get_E2E_latency(
                        self.mec_set, self.graph, start_node, target_node
                    )
                    
                    network_latency = latency.get('network_latency')
                    destination_latency = latency.get('destination_latency')
                    e2e_latency = latency.get('e2e_latency')
                    
                    total_net_latency += network_latency
                    total_computing_latency += destination_latency
                    total_e2e_latency += e2e_latency

                vr_controller.VrController.change_service_video_resolution(
                    self.mec_set, self.hmds_set, id, service_id, e2e_latency
                )
            
                services_cont += 1
        
        average_net_latency = round((total_net_latency / services_cont), 3)
        average_computing_latency = round((total_computing_latency / services_cont), 3)
        average_e2e_latency = round((total_e2e_latency / services_cont), 3)
        
        result = {
            "average_net_latency": average_net_latency,
            "average_computing_latency": average_computing_latency,
            "average_e2e_latency": average_e2e_latency
        }
        
        return result

    def offload_services(self) -> None:
        count = 0
        for hmd in self.hmds_set.values():
            for service_id in hmd.services_ids:
                extracted_service = vr_controller.VrController.remove_vr_service(
                    hmd, service_id
                )
                
                start_node = bs_controller.BaseStationController.get_base_station(
                    self.base_station_set, hmd.current_location
                )

                dst_mec_id, dst_mec = mec_controller.MecController.discover_mec(
                    self.base_station_set, 
                    self.mec_set, 
                    self.graph, 
                    start_node, 
                    extracted_service,
                )

                if dst_mec is not None:
                    mec_controller.MecController.deploy_service(dst_mec, extracted_service)
                else:
                    count+=1
                    print(f'\n*** service {extracted_service} could not be offloaded ***')
        if count > 1:
            print(f'could not offload {count} services')
            a = input("press any key to continue")

    def calculate_gpu_usage(self) -> float:
        total_services = len(self.hmds_set)
        total_gpus = 0

        for hmd in self.hmds_set.values():
            for service in hmd.services_set:
                total_gpus += service.quota.resources.gpu

        for mec in self.mec_set.values():
            for service in mec.services_set:
                if service.is_mobile:
                    total_gpus += service.quota.resources.gpu

        result = total_gpus / total_services
        return result
    
    def calculate_energy_usage(self) -> dict:
        """calculates the energy usage of all services deployed on MECs and HMDs"""
        
        hmd_energy = 0
        total_energy = 0
        total_services = 0
        
        for hmd in self.hmds_set.values():
            for service in hmd.services_set:
                total_energy += service.video_decoder.energy.energy_consumption
                total_services += 1
        
        if total_services > 0: 
            hmd_energy = round((total_energy / total_services), 2)
        
        for mec in self.mec_set.values():
            for service in mec.services_set:
                if service.is_mobile:
                    total_energy += service.video_decoder.energy.energy_consumption
                    total_services += 1
        
        total_energy = round((total_energy / total_services), 2)
        
        result = {
            'total_energy': total_energy,
            'hmd_energy': hmd_energy   
        }
        
        return result
    
    @staticmethod
    def get_vr_services_on_HMDs(hmds_set: Dict[str,'VrHMD'] )-> int:
        """gets all VrServices deployed on HMDs"""
        
        count  = 0
        for hmd in hmds_set.values():
            count += len(hmd.services_set)
        return count
    
    def get_resolution_settings(self) -> dict:
        """calcualtes the resolutions of all services deployed on MECs and HMDs"""
        
        resolutions = {
            '1080p': 0,
            '1440p': 0,
            '4k': 0,
            '8k': 0,
        }
        
        for hmd in self.hmds_set.values():
            for service in hmd.services_set:
                resolution_key = service.video_decoder.resolution.resolution
                resolutions[resolution_key] += 1
                
        for mec in self.mec_set.values():
            for service in mec.services_set:
                if service.is_mobile:
                    resolution_key = service.video_decoder.resolution.resolution
                    resolutions[resolution_key] += 1
                    
        #print('\n###################### RESOLUTIONS ##########################')
        #print(f'1k: {resolutions.get("1080p")} | 2k: {resolutions.get("1440p")} | 4k: {resolutions.get("4k")} | 8k: {resolutions.get("8k")}')
        #print('#############################################################')        
        return resolutions
        
    def load_data_sets(self) -> None: 
        """ loads the data sets of mecs, base stations, and hmds """
        
        CONFIG = config_controller.ConfigController.get_config()
        data_dir = CONFIG['SYSTEM']['DATA_DIR']
        mec_file = CONFIG['SYSTEM']['MEC_FILE']
        bs_file = CONFIG['SYSTEM']['BS_FILE']
        hmds_file = CONFIG['SYSTEM']['HMDS_FILE']
        overall_mecs = CONFIG['MEC_SERVERS']['OVERALL_MECS']
        services_per_user = CONFIG['SYSTEM']['SERVICE_PER_USER']
    
        mec_controller.MecController.init_mec_servers(overall_mecs)    
        self.mec_set = json_controller.DecoderController.decoding_to_dict(
            data_dir, mec_file
        )
        
        bs_controller.BaseStationController.init_base_stations(
            self.mec_set
        )
        vr_controller.VrController.init_hmds(
            services_per_user
        )
        
        self.base_station_set = json_controller.DecoderController.decoding_to_dict(
            data_dir, bs_file
        )
        self.hmds_set = json_controller.DecoderController.decoding_to_dict(
            data_dir, hmds_file
        )
        
        return 