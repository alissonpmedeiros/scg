from dataclasses import dataclass
from architecture import ScgController
from migration_algorithms import Migration
from mec.mec_controller import MecController
from migration_algorithms import SCG
import time
from pprint import pprint as pprint

from vr import VrService
from vr_controller import VrController





def start_system() -> None:
    scg = ScgController()
    scg_enabled = False
    #MecController.print_mecs(scg.base_station_set, scg.mec_set)
    
    migration = Migration()

    
    while True:
        '''
        '''
        VrController.check_vr_service_workload(scg.mec_set, scg.vr_users)
        MecController.check_mec_service_workload(scg.mec_set, scg.vr_users, scg_enabled)
        
        start = time.time()
        '''
        '''
        print("*** starting trade-off ***")
        SCG.trade_off(
                        base_station_set=scg.base_station_set, 
                        mec_set=scg.mec_set, 
                        vr_users=scg.vr_users, 
                        migration=migration,
                        hosts=scg.onos.hosts)
        print("*** finishing trade-off trade-off ***")
        average_latency = scg.caculate_average_ETE()
        print("\n #################################")
        print("AVERAGE LATENCY: {}".format(average_latency))
        print("SUCESSFUL MIGRATIONS: {}".format(migration.sucessful_migrations))
        print("UNSUCCESFUL MIGRATIONS: {}".format(migration.unsuccessful_migrations))
        end = time.time()
        print(f"Runtime of the program is {end - start}")
        scg.onos.reload_hosts()
if __name__=='__main__':
    start_system()
    
