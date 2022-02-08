from architecture import ScgController
from mec.mec_controller import MecController
from migration_algorithms import SCG
import time
from pprint import pprint as pprint

from vr import VrService
from vr_controller import VrController

def start_system() -> None:
    scg = ScgController()
    scg_enabled = False
    sucessful_migrations=0
    unsucessful_migrations=0
    MecController.print_mecs(scg.base_station_set, scg.mec_set)
    
    while True:
        '''
        '''
        VrController.check_vr_service_workload(scg.mec_set, scg.vr_users)
        MecController.check_mec_service_workload(scg.mec_set, scg.vr_users, scg_enabled)
        
        '''
        print("*** starting trade-off ***")
        SCG.trade_off(
                        base_station_set=scg.base_station_set, 
                        mec_set=scg.mec_set, 
                        vr_users=scg.vr_users, 
                        sucessful_migrations=sucessful_migrations, 
                        unsuccessful_migrations=unsucessful_migrations)
        print("*** finishing trade-off trade-off ***")
        '''
        average_latency = scg.caculate_average_ETE()
        print("\n AVERAGE LATENCY: {}".format(average_latency))
        print("\nSUCESSFUL MIGRATIONS: {}".format(sucessful_migrations))
        print("\nUNSUCCESFUL MIGRATIONS: {}".format(unsucessful_migrations))
        time.sleep(2)
        #a = input("")

if __name__=='__main__':
    start_system()
    
