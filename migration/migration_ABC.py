from abc import ABC
from vr.vr import VrService
from mec.mec import MecAgent


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
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        graph: dict, 
    ):
        for user in vr_users:
            if user.current_location != user.previous_location:
                for service_id in user.services_ids:
                    service = None
                    if any(service_id == service.id for service in user.services_set): 
                        service=user.services_set[0]
                    else: 
                        service = MecAgent.get_mec_service(mec_set, service_id)
                    self.service_migration(
                        base_station_set=base_station_set,
                        mec_set=mec_set,
                        vr_users=vr_users,
                        service=service,
                        graph=graph,
                    )
        
    def service_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        service: VrService,
        graph: dict,
    ) -> bool:
        pass    