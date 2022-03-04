from abc import ABC
from typing import List
from graph.graph import Graph
from vr.vr_hmd import VrHMD
from vr.vr_service import VrService
from mec.mec import Mec
from mec.mec_agent import MecAgent
from base_station.base_station import BaseStation


"""abstract base classes let you define a class with abstract methods, which all subclasses must implement in order to be initialized"""
class Migration(ABC):
    successful_migrations = 0
    unsuccessful_migrations = 0

    def get_migrations(self):

        success = self.successful_migrations
        unsuccess = self.unsuccessful_migrations

        self.successful_migrations = 0
        self.unsuccessful_migrations = 0

        return success, unsuccess

    def check_services(
        self,
        base_station_set: List[BaseStation],
        mec_set: List[Mec],
        vr_users: List[VrHMD],
        graph: Graph, 
    ):
        for user in vr_users:
            if user.current_location != user.previous_location:
                for service_id in user.services_ids:
                    service = None
                    if any(service_id == service.id for service in user.services_set): 
                        service=user.services_set[0]
                    else: 
                        service = MecAgent.get_mec_service(mec_set, service_id)
                    self.service_migration(
                        base_station_set=base_station_set,
                        mec_set=mec_set,
                        vr_users=vr_users,
                        graph=graph,
                        service=service,
                    )
        
    def service_migration(
        self,
        base_station_set: List[BaseStation],
        mec_set: List[Mec],
        vr_users: List[VrHMD],
        graph: Graph,
        service: VrService,
    ) -> bool:
        pass    