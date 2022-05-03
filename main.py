"""scg system imports"""
from migration.migration_ABC import Migration
from vr.vr_controller import VrController
from scg_controller.scg_controller import ScgController
from workloads.workload_controller import WorkloadController

"""service migration algorithms modules"""
from migration.algorithms.scg_tradeoff import SCG
from migration.algorithms.scg_react import ScgReact
from migration.algorithms.no_migration import NoMigration
from migration.algorithms.always_migrate import AlwaysMigrate
from migration.algorithms.net_latency import NetLatencyMigration
from migration.algorithms.net_latency_resource_aware import NetLatencyMigrationResouceAware

"""other imports"""
import time, sys
from pprint import pprint as pprint
from encoders.csv_encoder import CSV

FILE_NAME='{}.csv'.format(sys.argv[1])
FILE_DIR = '/home/ubuntu/scg/results/'


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
    elif sys.argv[1] == 'network-resource':
        return NetLatencyMigrationResouceAware()
    else:
        print('*** algorithm not found! ***')

def start_system(scg_controller: ScgController, migration_algorithm: Migration) -> list:
    while True:
        VrController.update_users_location(scg_controller.vr_users)
        WorkloadController.update_workloads(
            base_station_set=scg_controller.base_station_set,
            mec_set=scg_controller.mec_set, 
            vr_users=scg_controller.vr_users,
            migration=migration_algorithm,
            graph=scg_controller.graph,
        )
        migration_algorithm.check_services(
            base_station_set=scg_controller.base_station_set,
            mec_set=scg_controller.mec_set, 
            vr_users=scg_controller.vr_users,
            graph=scg_controller.graph,
        )
        net_latency, computing_latency, ete_latency = scg_controller.get_average_E2E_latency()
        gpu_usage = scg_controller.calculate_gpu_usage()
        successful_migration, unsuccessful_migration = migration_algorithm.get_migrations()
        energy_consumption = scg_controller.calculate_energy_usage()
        HMD_energy_consumption = scg_controller.calculate_HMD_energy_usage()
        services_on_hmds = scg_controller.get_vr_services_on_HMD()
        data = [gpu_usage, net_latency, computing_latency, ete_latency, successful_migration, unsuccessful_migration, energy_consumption, HMD_energy_consumption, services_on_hmds]
        
        #print(f'\n SERVICES ON HMDS: {scg_controller.get_vr_services_on_HMD()} \n')
        CSV.save_data(FILE_DIR, FILE_NAME, data)
        #a = input('')
        time.sleep(3)

if __name__ == "__main__":
    CSV.create_file(FILE_DIR, FILE_NAME)
    scg_controller = ScgController()
    migration_algorithm = check_algorithm()
    start_system(scg_controller, migration_algorithm)
    
