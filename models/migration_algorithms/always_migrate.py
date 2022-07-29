"""graph module"""
from models.graph import Graph
from controllers.mec_controller import MecController

"""vr modules"""
from models.vr import VrService, VrHMD
from controllers.vr_controller import VrController

"""mec modules"""
from models.mec import Mec 

"""migration module"""
from models.migration_ABC import Migration

"""base station modules"""
from models.base_station import BaseStation
from controllers.bs_controller import BaseStationController

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
        bs_mec = MecController.get_mec(mec_set, user_bs)

        if MecController.check_deployment(
            mec_set=mec_set, mec=bs_mec, service=service
        ):
            service_mec_server = MecController.get_service_mec_server(mec_set, service.id)
            extracted_service = MecController.remove_service(
                service_mec_server, service
            )
            MecController.deploy_service(bs_mec, extracted_service)
            self.successful_migrations += 1
            return True
        else:
            self.unsuccessful_migrations += 1
            return False




    