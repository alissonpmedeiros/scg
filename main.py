"""scg system imports"""
from migration.scg import SCG
from vr_controller import VrController
from workloads import WorkloadController
from scg_controller import ScgController
from migration.scg_react import ScgReact
from migration.no_migration import NoMigration
from migration.always_migrate import AlwaysMigrate
from migration.network_migration import NetLatencyMigration

"""other imports"""
import time, sys
from pprint import pprint as pprint


def check_algorithm():
    if sys.argv[1] == 'no':
        return NoMigration()
    elif sys.argv[1] == 'scg':
        return SCG()
    elif sys.argv[1] == 'always':
        return AlwaysMigrate()
    elif sys.argv[1] == 'react':
        return ScgReact()
    elif sys.argv[1] == 'network':
        return NetLatencyMigration()

def start_system(scg_controller, migration_algorithm) -> None:
    previous_latency = None
    while True:
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
    """variables"""
    scg_controller = ScgController()
    migration_algorithm = check_algorithm()
    start_system(scg_controller, migration_algorithm)

