import time
from abc import ABC
from vr import VrService
from mec.mec import MecAgent


"""abstract base classes let you define a class with abstract methods, which all subclasses must implement in order to be initialized"""
class Migration(ABC):
    sucessful_migrations = 0
    unsuccessful_migrations = 0

    def get_migrations(self):
        print("SUCESSFUL MIGRATIONS: {}".format(self.sucessful_migrations))
        print("UNSUCCESFUL MIGRATIONS: {}".format(self.unsuccessful_migrations))

    def check_services(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
    ):
        for user in vr_users:
            if user.current_location != user.previous_location:
                #print('UPDATING USER {} LOCATION: NEW {} | PREVIOUS: {}'.format(user.ip, user.current_location, user.previous_location))
                for service_id in user.services_ids:
                    service = None
                    if any(service_id == service.id for service in user.services_set): 
                        service=user.services_set[0]
                    else: 
                        service = MecAgent.get_service(mec_set, service_id)
                    self.service_migration(
                        base_station_set=base_station_set,
                        mec_set=mec_set,
                        vr_users=vr_users,
                        service=service,
                    )
        #time.sleep(0.5)
        


    def service_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        service: VrService
    ):
        pass    