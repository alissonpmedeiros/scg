"""scg system imports"""
from migration.migration import SCG
from migration.always_migrate import AlwaysMigrate
from workloads import WorkloadController
from scg import ScgController
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
    while True:
        # SERVICE MIGRATION ALGORITHM OBJECT MUST BE SPECIFIED HERE
        WorkloadController.check_workloads(
            base_station_set=scg_controller.base_station_set,
            mec_set=scg_controller.mec_set, 
            vr_users=scg_controller.vr_users,
            hosts=scg_controller.onos.hosts,
            migration=migration_algorithm,
        )
        migration_algorithm.check_services(
            base_station_set=scg_controller.base_station_set,
            mec_set=scg_controller.mec_set, 
            vr_users=scg_controller.vr_users,
            hosts=scg_controller.onos.hosts
        )


        #start = time.time()
        #end = time.time()
        migration_algorithm.get_migrations()
        latency = scg_controller.get_average_ETE_latency()
        print('ETE latency: {}'.format(latency))
        print('\n')
        scg_controller.onos.reload_hosts()


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