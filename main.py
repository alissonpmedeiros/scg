"""scg system imports"""
from migration.always_migrate import AlwaysMigrate
from migration.scg import SCG
from vr_controller import VrController
from workloads import WorkloadController
from scg_controller import ScgController
from mec.mec_controller import MecController

"""other imports"""
import time
from pprint import pprint as pprint


"""variables"""
scg_controller = ScgController()
migration_algorithm = SCG()

def start_system() -> None:
    #MecController.print_mecs(scg_controller.base_station_set, scg_controller.mec_set)
    #a = input()
    previous_latency = None
    while True:
        # SERVICE MIGRATION ALGORITHM OBJECT MUST BE SPECIFIED HERE
        WorkloadController.check_workloads(
            base_station_set=scg_controller.base_station_set,
            mec_set=scg_controller.mec_set, 
            vr_users=scg_controller.vr_users,
            migration=migration_algorithm,
        )
        migration_algorithm.check_services(
            base_station_set=scg_controller.base_station_set,
            mec_set=scg_controller.mec_set, 
            vr_users=scg_controller.vr_users,
        )


        #start = time.time()
        #end = time.time()
        latency = scg_controller.get_average_ETE_latency()
        
        if latency != previous_latency:
            migration_algorithm.get_migrations()
            print('ETE latency: {}'.format(latency))
            print('\n')
        
        previous_latency = latency
        

        VrController.update_users_location(scg_controller.vr_users)
        #pprint(scg_controller.vr_users)
        #a = input("")
        #scg_controller.onos.reload_hosts() WE NO LONGER NEED THIS METHOD
        # WE HAVE TO ADAPT THE WHOLE SYSTEM TO NOT USE THE RELOAD HOSTS ANYMORE. CHECK THE DEPENDENCIES. IT SHOULD BE REPLACED BY SCG_CONTROLER.VR_USERS

if __name__ == "__main__":
    start_system()

"""
ANALYZE THE FOLLOWING ASPECTS:
WITH REACT ENABLED
MIGRATION TRIGGERED BY COMPUTING LATENCY ANALYSIS
MIGRATION TRIGGERED BY NETWORK LATENCY ANALYSIS
NO MIGRATION
UAV MECHANISM


"""