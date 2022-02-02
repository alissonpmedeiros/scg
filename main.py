from architecture import ScgController
from mec.mec import MecController
from migration_algorithms import SCG
import time

def start_system() -> None:
    scg = ScgController()
    #MecController.print_mecs(scg.base_station_set, scg.mec_set)
    #a = input("start check migration!")
    '''
    while True:
        print("\n\n##############################\n")
        scg.service_migration()
        time.sleep(1)
    '''
    #pprint(scg.mec_set)
    #MecController.print_mecs(scg.base_station_set, scg.mec_set)
    '''
    while True:
        scg.service_migration('10.0.0.4', '27338475-ceba-4110-acc3-c2e10ffcfe61')
        time.sleep(0.5)
    '''
    #scg.reverse_offloading('10.0.0.4', '48cb9d0e-5c90-46c1-b357-7324123269a1')
    MecController.print_mecs(scg.base_station_set, scg.mec_set)
    while True:
        SCG.trade_off(base_station_set=scg.base_station_set, mec_set=scg.mec_set, vr_users=scg.vr_users)
        average_latency = scg.caculate_average_ETE()
        print("\n AVERAGE LATENCY: {} \n".format(average_latency))
        time.sleep(2)
        #a = input("")

if __name__=='__main__':
    start_system()