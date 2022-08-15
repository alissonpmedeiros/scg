import typing 
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.migration_ABC import Migration

from models.migration_algorithms.la import LA
from models.migration_algorithms.lra import LRA
from models.migration_algorithms.scg import SCG
from models.migration_algorithms.nm import NoMigration
from models.migration_algorithms.am import AlwaysMigrate

""" controllers modules """
from controllers import vr_controller 
from controllers import scg_controller 
from controllers import config_controller
from controllers import workload_controller


"""other imports"""
import sys, asyncio
from utils.csv_encoder import CSV

CONFIG = config_controller.ConfigController.get_config()
 
FILE_NAME='{}.csv'.format(sys.argv[1])
RESULTS_DIR = CONFIG['SYSTEM']['RESULTS_DIR']


def check_algorithm():
    if sys.argv[1] == 'no':
        return NoMigration()
    elif sys.argv[1] == 'scg':
        return SCG()
    elif sys.argv[1] == 'always':
        return AlwaysMigrate()
    elif sys.argv[1] == 'network':
        return LA()
    elif sys.argv[1] == 'network-resource':
        return LRA()
    else:
        print('*** algorithm not found! ***')
        
async def update_hmds_position(scg_controller: scg_controller.ScgController):
    print('\n*** UPDATING USERS LOCATION ***')
    while vr_controller.VrController.update_hmds_positions(scg_controller.hmds_set) is not None:
        await asyncio.sleep(0.00001)
    
async def update_workloads(scg_controller: scg_controller.ScgController, migration_algorithm: 'Migration'):
    print('\n*** UPDATING WORKLOADS ***')
    while workload_controller.WorkloadController.update_workloads(
        scg_controller.base_station_set,
        scg_controller.mec_set, 
        scg_controller.hmds_set,
        scg_controller.graph,
        migration_algorithm
    ) is not None:
        await asyncio.sleep(0.00001)

async def check_services(scg_controller: scg_controller.ScgController):
    print('\n*** CHECKING SERVICES ***')
    while migration_algorithm.check_services(
        scg_controller.base_station_set,
        scg_controller.mec_set, 
        scg_controller.hmds_set,
        scg_controller.graph,
    ) is not None:
        await asyncio.sleep(0.00001)

async def start_system(scg_controller: scg_controller.ScgController, migration_algorithm: 'Migration'):
    print('\n*** STARTING SYSTEM ***')
    while True:
        
        await update_hmds_position(scg_controller)
        await update_workloads(scg_controller, migration_algorithm)
        await asyncio.sleep(1)
        await check_services(scg_controller)
        
        latency = scg_controller.get_average_E2E_latency()
        average_net_latency = latency.get('average_net_latency')
        average_computing_latency = latency.get('average_computing_latency')
        average_e2e_latency = latency.get('average_e2e_latency')
        
        gpu_usage = scg_controller.calculate_gpu_usage()
        
        migrations = migration_algorithm.get_migrations()
        successful_migration = migrations.get('successful_migrations')
        unsuccessful_migration = migrations.get('unsuccessful_migrations')
        
        energy_consumption = scg_controller.calculate_energy_usage()
        
        total_energy_consumption = energy_consumption.get('total_energy')
        hmds_energy_consumption = energy_consumption.get('hmd_energy')
        
        services_on_hmds = scg_controller.get_vr_services_on_HMDs(scg_controller.hmds_set)
        
        resolution_metrics = scg_controller.get_resolution_settings()
        
        data = [
            gpu_usage, 
            average_net_latency, 
            average_computing_latency, 
            average_e2e_latency, 
            successful_migration,
            unsuccessful_migration, 
            total_energy_consumption, 
            hmds_energy_consumption, 
            services_on_hmds,
            resolution_metrics['8k'],
            resolution_metrics['4k'],
            resolution_metrics['1440p'],
            resolution_metrics['1080p']
        ]
        
        CSV.save_data(RESULTS_DIR, FILE_NAME, data)
        

if __name__ == "__main__":
    CSV.create_file(RESULTS_DIR, FILE_NAME)
    scg_controller = scg_controller.ScgController()
    migration_algorithm = check_algorithm()
    asyncio.run(start_system(scg_controller, migration_algorithm))
    
