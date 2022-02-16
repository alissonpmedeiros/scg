from vr import VrService
from graph import Dijkstra
from mec.mec import MecAgent
from migration.migration import Migration
from migration.react import REACTApproach
from base_station import BaseStationController
from mec.mec_controller import MecController
from migration.scg import SCG   

class ScgReact(SCG):
    """inherited from the SCG class"""
    def check_services(self, base_station_set: list, mec_set: list, vr_users: list):
        return super().check_services(base_station_set, mec_set, vr_users)

    """inherited from the SCG class"""
    def get_migrations(self):
        return super().get_migrations()

    """inherited from the SCG class"""
    def service_migration(
        self, base_station_set: list, mec_set: list, vr_users: list, service: VrService
    ):
        return super().service_migration(base_station_set, mec_set, vr_users, service)

    """inherited from the SCG class"""
    def reverse_offloading(
        self, mec_set: list, vr_users: list, user_ip: str, service_id: str
    ) -> None:
        return super().reverse_offloading(mec_set, vr_users, user_ip, service_id)

    """inherited from the SCG class"""
    def perform_migration(
        self, base_station_set: list, mec_set: list, vr_users: list, user_ip: str, service_id: str
    ):
        return super().perform_migration(base_station_set, mec_set, vr_users, user_ip, service_id)

    """inherited from the SCG class"""
    def trade_off(
        self, base_station_set: list, mec_set: list, vr_users: list, service: VrService
    ):
        return super().trade_off(base_station_set, mec_set, vr_users, service)

    """this method is not inherited from the SCG class, we rewrote it"""
    def discover_mec(
        self, base_station_set: list, mec_set: list, user: dict, service: VrService, 
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        ## SCG ##
        '''
        scg_shortest_latency = float("inf")
        scg_path = []
        for base_station in base_station_set:
            if ( 
                MecAgent.check_deployment(
                    mec_set, base_station.mec_id, service
                )
            ):
                """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
                src_bs = BaseStationController.get_base_station(
                    base_station_set, current_base_station.id
                )
                src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
                aux_path, new_latency = Dijkstra.init_algorithm(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    start_node=current_base_station.id,
                    start_node_computing_delay=src_mec.computing_latency,
                    target_node=base_station.id,
                )

                if new_latency <= scg_shortest_latency:
                    scg_path = aux_path
                    scg_shortest_latency = new_latency

        """ we need to take care of the case where there is no more mec available """
        if not scg_path:
            return None

        # print(" -> ".join(path))
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        scg_bs_destination = BaseStationController.get_base_station(
            base_station_set, scg_path[-1]
        )

        '''
        ## REACT ##
        shortest_latency = float("inf")
        mec_id_candidate = None
        path = []
        for base_station in base_station_set:
            """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
            src_bs = BaseStationController.get_base_station(
                base_station_set, current_base_station.id
            )
            src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
            aux_path, new_latency = Dijkstra.init_algorithm(
                base_station_set=base_station_set,
                mec_set=mec_set,
                start_node=current_base_station.id,
                start_node_computing_delay=src_mec.computing_latency,
                target_node=base_station.id,
            )

            if new_latency <= shortest_latency:
                path = aux_path
                shortest_latency = new_latency
                mec_id_candidate = base_station.mec_id
            
        """ we need to take care of the case where there are no more mec available """
        if not path:
            return None
        
        if not (
            MecAgent.check_deployment(
                mec_set, mec_id_candidate, service
            )
        ):
            #print('REACT ENABLED!')
            REACTApproach.solidarity(
                mec_set=mec_set, 
                mec_id=mec_id_candidate, 
                service=service, 
                sucessful_migrations=self.sucessful_migrations, 
                unsuccessful_migrations=self.unsuccessful_migrations
            )
        

        # print(" -> ".join(path))
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )

        '''
        if scg_bs_destination!= bs_destination:
            print('\nDIFFERENT DESTINATIONS')
            print('SCG DESTINATION: ')
            print(" -> ".join(scg_path))
            print("latency: {}".format(scg_shortest_latency))
            print('\nREACT DESTINATION: ')
            print(" -> ".join(path))
            print("latency: {}".format(shortest_latency))

            print('\n')
            a = input('')
        '''
        return bs_destination.mec_id