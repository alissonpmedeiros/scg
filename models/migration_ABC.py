import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 

""" controller modules """
from controllers import mec_controller

""" other modules """
from abc import ABC
from typing import Dict


"""abstract base classes let you define a class with abstract methods, which all subclasses must implement in order to be initialized"""
class Migration(ABC):
    successful_migrations = 0
    unsuccessful_migrations = 0

    def get_migrations(self) -> dict:

        success = self.successful_migrations
        unsuccess = self.unsuccessful_migrations

        self.successful_migrations = 0
        self.unsuccessful_migrations = 0

        result = {
            'successful_migrations': success,
            'unsuccessful_migrations': unsuccess,
        }

        return result

    def check_services(
        self,
        base_station_set: Dict[str,'BaseStation'],
        mec_set: Dict[str,'Mec'],
        hmds_set: Dict[str,'VrHMD'],
        graph: 'Graph', 
    ) -> None:
        #print('\n################### START SERVICE CHECK #######################')
        for hmd in hmds_set.values():
            if hmd.current_location != hmd.previous_location:
                for service_id in hmd.services_ids:
                    service = None 
                    if any(service_id == vr_service.id for vr_service in hmd.services_set): 
                        service_index = [vr_service.id for vr_service in hmd.services_set].index(service_id)
                        service = hmd.services_set[service_index]
                    else: 
                        service = mec_controller.MecController.get_mec_service(mec_set, service_id)
                    
                    self.service_migration(
                        base_station_set, mec_set, hmds_set, graph, service
                    )
        #print('\n################### FINISH SERVICE CHECK #######################')
        return
        
    def service_migration(
        self,
        base_station_set: Dict[str,'BaseStation'],
        mec_set: Dict[str,'Mec'],
        hmds_set: Dict[str,'VrHMD'],
        graph: 'Graph',
        service: 'VrService',
    ) -> bool:
        pass    