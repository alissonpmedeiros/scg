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
                print('UPDATING USER {} LOCATION: NEW {} | PREVIOUS: {}'.format(user.ip, user.current_location, user.previous_location))
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
        time.sleep(0.5)
        


    def service_migration(
        self,
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        service: VrService
    ):
        pass    


'''
class REACT(Migration):
    
    @staticmethod
    def service_migration(
        base_station_set: list,
        mec_set: list,
        vr_users: list,
        migration: MigrationController,
        service: VrService,
    ):
        REACTApproach.solidarity(
            mec_set=mec_set, 
            current_mec_id='TBD', ### TO BE DEFINED! 
            service=service,
        )

# TO ANALYZE THE IMPACT OF REACT, WE HAVE TO ADAPT THE SYSTEM DO CATCH A SITUATION WHERE THE BEST SERVER IS ALWAYS CONSIDER, REGARDLESS THE RESOURCE AVAILABILITY            



class NoMigration(Migration):
    """ implements the no migration behaviour """

    def service_migration(base_station_set: list, mec_set: list, vr_users: list):
        pass


class NetLatencyMigration(Migration):
    """ implements the migration behaviour based on net latency """

    def service_migration(base_station_set: list, mec_set: list, vr_users: list):
        pass


class AUB(Migration):
    """ implements the algorithm Average Utilization Based (AUB) Migration """

    def service_migration(base_station_set: list, mec_set: list, vr_users: list):
        pass

        """ 
        Describe the algorithm: 
        (i) SFCs should be placed on the paths where link latency is as optimal as possible; 
        (ii) processing capacity of VNFs can be improved to reduce response latency by allocating more resources to those VNFs. AUB only considers (ii), while SCG consider both. 
        
        1. Both under-utilized and over-utilized servers are first identified
        2. For each over-utilized server, one or more VNFs are selected as victim VNFs based on Eq. (20
        3. Afterwards, optimal servers are chosen from under-utilized servers for these victim VNFs using policy of choosing target server
        4.
        """

'''