from vr import VrService
from graph import Dijkstra
from mec.mec import MecAgent
from vr_controller import VrController
from scg_controller import ScgController
from migration.migration import Migration
from base_station import BaseStationController
from mec.mec_controller import MecController


class SCG(Migration):    

    def check_services(self, base_station_set: list, mec_set: list, vr_users: list):
        return super().check_services(base_station_set, mec_set, vr_users)

    def get_migrations(self):
        return super().get_migrations()
        

    def service_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list, 
        service: VrService,
    ):
        self.trade_off(
            base_station_set=base_station_set,
            mec_set=mec_set,
            vr_users=vr_users,
            service=service,
        )
        

    
    def reverse_offloading(
        self, 
        mec_set: list, 
        vr_users: list, 
        user: dict, 
        service: VrService
    ) -> None:
        """ offloads a service i back to vr hmd """

        service_server_id = MecAgent.get_service_server_id(mec_set, service.id)
        extracted_service = MecAgent.remove_service(
            mec_set, service_server_id, service.id
        )

        VrController.deploy_vr_service(
            vr_users=vr_users, user_ip=user.ip, service=extracted_service
        )

    """ ADJUST THIS METHOD TO USE ONLY CALCULATE NET LATENCY INSTEAD OF ETE LATENCY. THEN, THIS METHOD SHOULD BE USED WIHTIN CLASS 'NetLatencyMigration' """
    
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
        

        service_server_id = MecAgent.get_service_server_id(mec_set, service.id)
        service_location = MecAgent.get_service_bs_location(
            base_station_set, mec_set, service.id
        )
        computing_latency, network_latency, previous_service_latency = ScgController.get_ETE_latency(
            base_station_set=base_station_set,
            mec_set=mec_set,
            src_location=user.current_location,
            dst_location=service_location,
        )

        mec_id_candidate = self.discover_mec(
            base_station_set=base_station_set,
            mec_set=mec_set,
            user=user,
            service=service,
        )

        if mec_id_candidate is not None:
            mec_candidate_location = MecAgent.get_mec_bs_location(
                base_station_set, mec_id_candidate
            )
            computing_latency, network_latency, new_service_latency = ScgController.get_ETE_latency(
                base_station_set=base_station_set,
                mec_set=mec_set,
                src_location=user.current_location,
                dst_location=mec_candidate_location,
            )

            if new_service_latency < previous_service_latency:
                extracted_service = MecAgent.remove_service(
                    mec_set, service_server_id, service.id
                )
                MecAgent.deploy_service(mec_set, mec_id_candidate, extracted_service)
                #print("*** Performing migration ***")
                # print("service {} move from MEC {} to {}".format(service_id, service_server_id, mec_id_candidate))
                # print("new latency: {}\n".format(new_service_latency))
                self.sucessful_migrations += 1

        else:
            print("*** Migration failed. Error: no candidates ***")
            self.unsuccessful_migrations += 1

    
    def trade_off(
        self, 
        base_station_set: list, 
        mec_set: list, 
        vr_users: list,
        service: VrService,
    ):
        """ provide the trade-off analysis between migration and offloading the service back to the HMD"""

        service_owner = VrController.get_vr_service_owner(
            vr_users=vr_users, service=service
        )
        
        
        if any(service.id == user_service.id for user_service in service_owner.services_set):
            """ checks whether a service IS deployed on the HMD """
            hmd_latency = VrController.get_hmd_latency(
                base_station_set=base_station_set,
                vr_users=vr_users,
                user_ip=service_owner.ip,
            )


            mec_id_candidate = self.discover_mec(
                base_station_set=base_station_set,
                mec_set=mec_set,
                user=service_owner,
                service=service,
            )


            if mec_id_candidate is not None:
                mec_candidate_location = MecAgent.get_mec_bs_location(
                    base_station_set, mec_id_candidate
                )
                computing_latency, network_latency, new_service_latency = ScgController.get_ETE_latency(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    src_location=service_owner.current_location,
                    dst_location=mec_candidate_location,
                )

                if new_service_latency < hmd_latency:
                    extracted_service = VrController.remove_vr_service(
                        vr_users=vr_users,
                        user_ip=service_owner.ip,
                        service_id=service.id,
                    )

                    MecAgent.deploy_service(
                        mec_set, mec_id_candidate, extracted_service
                    )
                    # Performing offloading ***")
                    # print("service {} move from HMD {} to MEC {}".format(service_id, user.ip, mec_id_candidate))
                    # print("hmd latency: {}".format(hmd_latency))
                    # print("new latency: {}\n".format(new_service_latency))
                    # a = input("")

            else:
                #print("**** no candidates ****")
                """
                Migration should be considered. However, there are no mec servers available. 
                The service stays on the HMD. 
                We should consider a service migration violation... 
                """

        else:
            """ otherwise, the service is deployed on MEC servers"""
            service_location = MecAgent.get_service_bs_location(
                base_station_set, mec_set, service.id
            )

            """ 
            measures the latency between bs where the user 
            is connected and the mec where the service is deployed 
            """
            '''
            '''
            if service_location is None or service_owner.current_location is None:
                print("\nservice ID: {}".format(service.id))
                print("\nservice location: {}".format(service_location))
                print("\nservice owner: {}".format(service_owner))
                print("\nservice owner location: {}".format(service_owner.current_location))
                print(
                    "GOT AN ERROR: SERVICE LOCATION OR USER LOCATION NOT FOUND!"
                )
                a = input("")

            computing_latency, network_latency, current_service_latency = ScgController.get_ETE_latency(
                base_station_set=base_station_set,
                mec_set=mec_set,
                src_location=service_owner.current_location,
                dst_location=service_location,
            )

            hmd_latency = VrController.get_hmd_latency(
                base_station_set=base_station_set,
                vr_users=vr_users,
                user_ip=service_owner.ip,
            )

            # print('\n')
            # print('service id: {}'.format(service_id))
            # print('service location: {}'.format(service_location))
            # print('service latency: {}'.format(current_service_latency))
            # print('hmd {} has latency: {}'.format(user.ip, hmd_latency))

            if current_service_latency <= hmd_latency:
                # print('service remains on mec servers. \nstarting migration check')
                self.perform_migration(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    vr_users=vr_users,
                    user=service_owner,
                    service=service,
                )
            else:
                #print("*** Performing reverse offloading ***")
                self.reverse_offloading(
                    mec_set=mec_set,
                    vr_users=vr_users,
                    user=service_owner,
                    service=service,
                )




    def discover_mec(
        self, base_station_set: list, mec_set: list, user: dict, service: VrService, 
    ) -> str:
        """ discovers a nearby MEC server to either offload or migrate the service"""

        shortest_latency = float("inf")
        path = []
        for base_station in base_station_set:
            if ( 
                MecAgent.check_deployment(
                    mec_set, base_station.mec_id, service
                )
            ):
                """ tests if the mec attached to the base station can deploy the service"""
                src_bs = BaseStationController.get_base_station(
                    base_station_set, user.current_location
                )
                src_mec = MecController.get_mec(mec_set, src_bs.mec_id)
                aux_path, new_latency = Dijkstra.init_algorithm(
                    base_station_set=base_station_set,
                    mec_set=mec_set,
                    start_node=user.current_location,
                    start_node_computing_delay=src_mec.computing_latency,
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