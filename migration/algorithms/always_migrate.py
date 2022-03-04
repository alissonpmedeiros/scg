"""graph module"""
from graph.graph import Graph

"""vr modules"""
from vr.vr_hmd import VrHMD
from vr.vr_service import VrService
from vr.vr_controller import VrController

"""mec modules"""
from mec.mec import Mec 
from mec.mec_agent import MecAgent

"""migration module"""
from migration.migration_ABC import Migration

"""base station modules"""
from base_station.base_station import BaseStation
from base_station.bs_controller import BaseStationController

"""other imports"""
from typing import List

class AlwaysMigrate(Migration):
    """ implements the migration behaviour trigered by handover """


    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph
    ):
        return super().check_services(base_station_set, mec_set, vr_users, graph)
    
    
    def service_migration(
        self, 
        base_station_set: List[BaseStation], 
        mec_set: List[Mec], 
        vr_users: List[VrHMD],
        graph: Graph,
        service: VrService,
     ) -> bool:
        
        service_owner = VrController.get_vr_service_owner(
            vr_users=vr_users, service=service
        )
        
        return self.perform_migration(
            base_station_set=base_station_set,
            mec_set=mec_set,
            user=service_owner,
            service=service,
        )
            
    def perform_migration(
        self,
        base_station_set: List[BaseStation],
        mec_set: List[Mec],
        user: VrHMD,
        service: VrService,
    ) -> bool:
        """
        provides the service migration of service i, which is based on the
        current distance between user_ip and where the service is deployed
        """

        user_bs = BaseStationController.get_base_station(
            base_station_set=base_station_set, bs_id=user.current_location
        )


        if MecAgent.check_deployment(
            mec_set=mec_set, mec_id=user_bs.mec_id, service=service
        ):
            service_server_id = MecAgent.get_service_server_id(mec_set, service.id)
            extracted_service = MecAgent.remove_service(
                mec_set, service_server_id, service.id
            )
            MecAgent.deploy_service(mec_set, user_bs.mec_id, extracted_service)
            self.successful_migrations += 1
            return True
        else:
            self.unsuccessful_migrations += 1
            return False




    