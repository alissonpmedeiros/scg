from vr import VrService
from mec.mec import MecAgent
import random

class REACT:

    @staticmethod
    def solidarity_approach(mec_set: list, current_mec_id: str, extracted_service: VrService):
        print('*** entering REACT ***')
        service_cpu = extracted_service.quota.resources.cpu
        service_gpu = extracted_service.quota.resources.gpu

        target_cpu = 0
        target_gpu = 0
        
        removed_service_set = []

        """ remove services from the mec where the service has to be deployed """
        """ CODE IS STUCKING HERE BECAUSE WE REMOVED ALL NON MOBILE SERVICES, 
        WE HAVE ENABLE IT AGAIN A FIND A WAY TO HAVE BOTH SERVICE TYPES ON THE SYSTEM """
        
        """ migrating services to deploy a more important sevice """
        while target_cpu <= service_cpu and target_gpu <= service_gpu:
            for mec in mec_set:
                if mec.id == current_mec_id:
                    for service in mec.services_set:
                        if not service.is_mobile:
                            service_cpu += service.quota.resources.cpu
                            service_gpu += service.quota.resources.gpu
                            removed_service = MecAgent.remove_service(
                                                                    mec_set,  
                                                                    current_mec_id, 
                                                                    service.id)
                            removed_service.append(removed_service)

            """ after migration the services, deploy the extracted service """
            MecAgent.deploy_service(
                                    mec_set=mec_set,
                                    mec_id=current_mec_id,
                                    service=extracted_service)
            
            
            """ 
            now we need to redistribute the removed service from the previous mec to new victims mecs 
            """
            
        while not removed_service_set:
            """ picks up a specific non mobile service that was catched in the previous step """
            removed_service = removed_service_set.pop()
            
            """ selects a random mec victim """
            victim_mec_index = 0
            while True:
                victim_mec_index = random.randint(0,27)
                if mec_set[victim_mec_index].id != current_mec_id.id and MecAgent.check_deployment(
                                mec_set=mec_set,
                                mec_id=victim_mec_index,
                                service=removed_service):
                    break
            
            MecAgent.deploy_service(
                                    mec_set=mec_set,
                                    mec_id=mec_set[victim_mec_index].id,
                                    service=removed_service)
            
        print('*** EXIT REACT ***')        

                  