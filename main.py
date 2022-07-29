import typing 
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.migration_ABC import Migration as Migration

#from models import Migration, SCG, NoMigration, AlwaysMigrate, NetLatencyMigration, NetLatencyMigrationResouceAware
from models.migration_algorithms.scg_tradeoff import SCG as SCG

""" controllers modules """
from controllers import vr_controller as vr
from controllers import scg_controller as scg
from controllers import config_controller as config
from controllers import workload_controller as workload


"""other imports"""
import time, sys, asyncio
from pprint import pprint as pprint
from utils.csv_encoder import CSV

CONFIG = config.ConfigController.get_config()
 
FILE_NAME='{}.csv'.format(sys.argv[1])
RESULTS_DIR = CONFIG['SYSTEM']['RESULTS_DIR']




def check_algorithm():
    return SCG()
    '''if sys.argv[1] == 'no':
        return NoMigration()
    elif sys.argv[1] == 'scg':
        return SCG()
    elif sys.argv[1] == 'always':
        return AlwaysMigrate()
    elif sys.argv[1] == 'network':
        return NetLatencyMigration()
    elif sys.argv[1] == 'network-resource':
        return NetLatencyMigrationResouceAware()
    else:
        print('*** algorithm not found! ***')'''
        
async def update_users_location(scg_controller: scg.ScgController):
    print('\n***UPDATING USERS LOCATION ***')
    while vr.VrController.update_users_location(scg_controller.vr_users) is not None:
        await asyncio.sleep(0.00001)
    
async def update_workloads(scg_controller: scg.ScgController, migration_algorithm: 'Migration'):
    print('\n***UPDATING WORKLOADS ***')
    while workload.WorkloadController.update_workloads(
        scg_controller.base_station_set,
        scg_controller.mec_set, 
        scg_controller.vr_users,
        scg_controller.graph,
        migration_algorithm
    ) is not None:
        await asyncio.sleep(0.00001)

async def check_services(scg_controller: scg.ScgController):
    print('\n***CHECKING SERVICES ***')
    while migration_algorithm.check_services(
        scg_controller.base_station_set,
        scg_controller.mec_set, 
        scg_controller.vr_users,
        scg_controller.graph,
    ) is not None:
        await asyncio.sleep(0.00001)

async def start_system(scg_controller: scg.ScgController, migration_algorithm: 'Migration'):
    print('\n***STARTING SYSTEM ***')
    while True:
        
        await update_users_location(scg_controller)
        await update_workloads(scg_controller, migration_algorithm)
        await asyncio.sleep(1)
        await check_services(scg_controller)
        await asyncio.sleep(1)
        
        net_latency, computing_latency, ete_latency = scg_controller.get_average_E2E_latency()
        gpu_usage = scg_controller.calculate_gpu_usage()
        successful_migration, unsuccessful_migration = migration_algorithm.get_migrations()
        energy_consumption = scg_controller.calculate_energy_usage()
        HMD_energy_consumption = scg_controller.calculate_HMD_energy_usage()
        services_on_hmds = scg.ScgController.get_vr_services_on_HMD(scg_controller.vr_users)
        data = [
            gpu_usage, 
            net_latency, 
            computing_latency, 
            ete_latency, 
            successful_migration,
            unsuccessful_migration, 
            energy_consumption, 
            HMD_energy_consumption, 
            services_on_hmds
        ]
        #print('end to end latency: {}'.format(ete_latency))
        #print('energy usage: {}'.format(energy_consumption))
        #scg_controller.calculate_resolution_usage()
        
        #print(f'\n SERVICES ON HMDS: {scg_controller.get_vr_services_on_HMD()} \n')
        CSV.save_data(RESULTS_DIR, FILE_NAME, data)
        #

if __name__ == "__main__":
    
    CSV.create_file(RESULTS_DIR, FILE_NAME)
    scg_controller = scg.ScgController()
    migration_algorithm = check_algorithm()
    asyncio.run(start_system(scg_controller, migration_algorithm))
    
