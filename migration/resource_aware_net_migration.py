from vr import VrService
from mec.mec import MecAgent
from vr_controller import VrController
from base_station import BaseStationController
from migration.net_latency_migration import NetLatencyMigration
from migration.net_latency_migration import Dijkstra



class ResourceAwareNetMigration(NetLatencyMigration):
    """inherited NetLatencyMigration class"""
    def get_migrations(self):
        return super().get_migrations()
    
    """inherited NetLatencyMigration class"""
    def check_services(self, base_station_set: list, mec_set: list, vr_users: list):
        return super().check_services(base_station_set, mec_set, vr_users)

    """inherited NetLatencyMigration class"""
    def service_migration(self, base_station_set: list, mec_set: list, vr_users: list, service: VrService):
        return super().service_migration(base_station_set, mec_set, vr_users, service)

    """this method is not inherited from NetLatencyMigration class, we rewrote it to make it a resource-aware algorithm"""
    def perform_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        user: dict,
        service: VrService,
    ):
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """

        service_bs_location = MecAgent.get_service_bs_location(
            base_station_set, mec_set, service.id
        )
        
        if user.current_location != service_bs_location:
            service_owner = VrController.get_vr_service_owner(
                vr_users=vr_users, service=service
            )
            mec_id_candidate = self.discover_mec(
                base_station_set=base_station_set,
                mec_set=mec_set,
                user=service_owner,
                service=service,
            )
            
            if mec_id_candidate is not None:
                service_server_id = MecAgent.get_service_server_id(
                    mec_set, service.id
                )
                extracted_service = MecAgent.remove_service(
                    mec_set, service_server_id, service.id
                )
                MecAgent.deploy_service(
                    mec_set, mec_id_candidate, extracted_service
                )
                self.sucessful_migrations += 1
            else:
                self.unsuccessful_migrations += 1

    """this method is not inherited from NetLatencyMigration class, we rewrote it to make it a resource-aware algorithm"""
    def discover_mec(
        self, base_station_set: list, mec_set: list, user: dict, service: VrService, 
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""


        current_base_station = BaseStationController.get_base_station(
            base_station_set, user.current_location
        )

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            if (
                MecAgent.check_deployment(
                    mec_set, base_station.mec_id, service
                )
            ):
                """ tests if the base station is not the source base station and the mec attached to the base station instance can deploy the service  """
                aux_path, new_latency = Dijkstra.init_algorithm(
                    base_station_set=base_station_set,
                    start_node=current_base_station.id,
                    target_node=base_station.id,
                )

                if new_latency <= shortest_latency:
                    path = aux_path
                    shortest_latency = new_latency

        """ we need to take care of the case where there is no more mec available """
        if not path:
            return None

        # print(" -> ".join(path))
        """ gets last element of the path, which corresponds to the base station which contains a mec server that can accomodate the service """
        bs_destination = BaseStationController.get_base_station(
            base_station_set, path[-1]
        )
        return bs_destination.mec_id 