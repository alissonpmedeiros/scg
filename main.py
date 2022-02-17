"""scg system imports"""
from migration.scg import SCG
from vr_controller import VrController
from workloads import WorkloadController
from scg_controller import ScgController
from migration.scg_react import ScgReact
from migration.no_migration import NoMigration
from migration.always_migrate import AlwaysMigrate
from migration.network_migration import MigrationBasedNetwork

"""other imports"""
import time, sys
from pprint import pprint as pprint


"""variables"""
scg_controller = ScgController()
migration_algorithm = None

if sys.argv[1] == 'no':
    migration_algorithm=NoMigration()
elif sys.argv[1] == 'scg':
    migration_algorithm=SCG()
elif sys.argv[1] == 'always':
    migration_algorithm=AlwaysMigrate()
elif sys.argv[1] == 'react':
    migration_algorithm=ScgReact()
elif sys.argv[1] == 'network':
    migration_algorithm=MigrationBasedNetwork()

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
            gpu_usage = scg_controller.calculate_gpu_usage()
            print("GPU USAGE: {}".format(gpu_usage))
            migration_algorithm.get_migrations()
            print('AVERAGE ETE LATENCY: {}'.format(latency))
            print('\n')
        
        previous_latency = latency
        

        VrController.update_users_location(scg_controller.vr_users)

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