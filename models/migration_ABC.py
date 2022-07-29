import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 

""" controller modules """
from controllers import mec_controller as mec

""" other modules """
from abc import ABC
from typing import List

"""abstract base classes let you define a class with abstract methods, which all subclasses must implement in order to be initialized"""
class Migration(ABC):
    successful_migrations = 0
    unsuccessful_migrations = 0

    def get_migrations(self):

        success = self.successful_migrations
        unsuccess = self.unsuccessful_migrations

        self.successful_migrations = 0
        self.unsuccessful_migrations = 0

        return success, unsuccess

    def check_services(
        self,
        base_station_set: List['BaseStation'],
        mec_set: List['Mec'],
        vr_users: List['VrHMD'],
        graph: 'Graph', 
    ) -> None:
        #print('\n################### START SERVICE CHECK #######################')
        for user in vr_users:
            if user.current_location != user.previous_location:
                for service_id in user.services_ids:
                    service = None 
                    if any(service_id == vr_service.id for vr_service in user.services_set): 
                        service=user.services_set[0]
                    else: 
                        service = mec.MecController.get_mec_service(mec_set, service_id)
                    self.service_migration(
                        base_station_set=base_station_set,
                        mec_set=mec_set,
                        vr_users=vr_users,
                        graph=graph,
                        service=service,
                    )
        #print('\n################### FINISH SERVICE CHECK #######################')
        return
        
    def service_migration(
        self,
        base_station_set: List['BaseStation'],
        mec_set: List['Mec'],
        vr_users: List['VrHMD'],
        graph: 'Graph',
        service: 'VrService',
    ) -> bool:
        pass    