import typing 
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.migration_ABC import Migration

from models.migration_algorithms.la import LA
from models.migration_algorithms.lra import LRA
from models.migration_algorithms.scg import SCG
from models.migration_algorithms.dscp import DSCP
from models.migration_algorithms.nm import NoMigration
from models.migration_algorithms.am import AlwaysMigrate

""" controllers modules """
from controllers import vr_controller 
from controllers import scg_controller 
from controllers import config_controller
from controllers import workload_controller


"""other imports"""
import sys, asyncio
from time import time
from utils.csv_encoder import CSV

CONFIG = config_controller.ConfigController.get_config()
 
FILE_NAME = '{}.csv'.format(sys.argv[1])
FILE_HEADER = [
    'gpu_usage', 
    'net_latency', 
    'comput_latency', 
    'ete_latency', 
    'successful', 
    'unsuccessful', 
    'energy', 
    'hmd_energy', 
    'services_on_hmds', 
    'exec', 
    '8k', 
    '4k', 
    '1440p', 
    '1080p'
]

RESULTS_DIR = CONFIG['SYSTEM']['RESULTS_DIR']


def check_algorithm():
    if sys.argv[1] == 'no':
        return NoMigration()
    elif sys.argv[1] == 'scg':
        return SCG()
    elif sys.argv[1] == 'am':
        return AlwaysMigrate()
    elif sys.argv[1] == 'la':
        return LA()
    elif sys.argv[1] == 'lra':
        return LRA()
    elif sys.argv[1] == 'dscp':
        return DSCP()
    else:
        print('*** algorithm not found! ***')
        a = input('')
        
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
        start = time()
        await check_services(scg_controller)
        end = time()
    
        execution_time = round((end - start), 2) 
        
        #print(f'calculating E2E latency')
        latency = scg_controller.get_average_E2E_latency()
        average_net_latency = latency.get('average_net_latency')
        average_computing_latency = latency.get('average_computing_latency')
        average_e2e_latency = latency.get('average_e2e_latency')
        
        #print(f'calculating gpu usage')
        gpu_usage = scg_controller.calculate_gpu_usage()
        
        #print(f'getting migrations')
        migrations = migration_algorithm.get_migrations()
        successful_migration = migrations.get('successful_migrations')
        unsuccessful_migration = migrations.get('unsuccessful_migrations')
        
        #print(f'calculating energy consumption')
        energy_consumption = scg_controller.calculate_energy_usage()
        
        total_energy_consumption = energy_consumption.get('total_energy')
        hmds_energy_consumption = energy_consumption.get('hmd_energy')
        
        #print(f'getting services on HMDs')
        services_on_hmds = scg_controller.get_vr_services_on_HMDs(scg_controller.hmds_set)
        
        #print(f'getting resolution metrics')
        resolution_metrics = scg_controller.get_resolution_settings()
        
        #print(f'saving the data...')
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
            execution_time,
            resolution_metrics['8k'],
            resolution_metrics['4k'],
            resolution_metrics['1440p'],
            resolution_metrics['1080p']
        ]
        
        CSV.save_data(RESULTS_DIR, FILE_NAME, data)
        

if __name__ == "__main__":
    CSV.create_file(RESULTS_DIR, FILE_NAME, FILE_HEADER)
    scg_controller = scg_controller.ScgController()
    migration_algorithm = check_algorithm()
    asyncio.run(start_system(scg_controller, migration_algorithm))
    #TODO:
    """
    1. Fix the trade-off feature to generate new trade-off plots for each topology
    2. from results csv file, calculate everything needed to generate a new csv file as input to overleaf
    3. increasing the radius for each topologies, which means different radius for each topology and different plots as well (DONE)
    4. average number of links per each vertice (DONE)
    5. delay on the links depends on the traffic of the links, because a congested link would trigger the algorithm to select another path to fulfill the latency requirements (TBD)
    6- model the problem as a markov decision process as the next decision depends on the previous decision. (TBD)
    """
 
 #TODO: store the algorithm files directly on the respective directories according to each radius