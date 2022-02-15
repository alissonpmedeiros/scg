from mec.mec import MecAgent
from vr import VrService
import random

class REACTApproach:

    @staticmethod
    def get_victim_services(mec_set: list, current_mec_id: str, service: VrService) -> list:
        target_cpu = 0
        target_gpu = 0
        victim_service_set = []
        
        """ remove services from the current mec where the service has to be deployed """
        for mec in mec_set:
            if mec.id == current_mec_id:
                for service in mec.services_set:
                    if not service.is_mobile:
                        target_cpu += service.quota.resources.cpu
                        target_gpu += service.quota.resources.gpu
                        removed_service = MecAgent.remove_service(
                            mec_set,  
                            current_mec_id, 
                            service.id
                        )
                        victim_service_set.append(removed_service)
                        if target_cpu >= service.quota.resources.cpu and target_gpu >= service.quota.resources.gpu:
                            break
                        

        """ after removing the victim services, deploy the current service """
        MecAgent.deploy_service(
            mec_set=mec_set,
            mec_id=current_mec_id,
            service=service
        )
        
        return victim_service_set
    

    @staticmethod
    def solidarity(mec_set: list, current_mec_id: str, service: VrService):
        """ 
        now we need to redistribute the removed service from the previous mec to new victims mecs 
        """
        victim_service_set = REACTApproach.get_victim_services(
            mec_set=mec_set,
            current_mec_id=current_mec_id,
            service=service,
        )

        while victim_service_set:
            """ picks up a specific non mobile service that will be migrated to a random mec server """
            removed_service = victim_service_set.pop()
            
            """ selects a random mec victim """
            victim_mec_index = 0
            while True:
                victim_mec_index = random.randint(0,27)
                if mec_set[victim_mec_index].id != current_mec_id and MecAgent.check_deployment(
                    mec_set=mec_set,
                    mec_id=mec_set[victim_mec_index].id,
                    service=removed_service
                ):
                    """at this point we found out the victim mec index to deploy the removed_service"""
                    break
        
            MecAgent.deploy_service(
                mec_set=mec_set,
                mec_id=mec_set[victim_mec_index].id,
                service=removed_service
            )
            
    

                  