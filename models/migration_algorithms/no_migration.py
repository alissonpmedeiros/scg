'''"""graph module"""
from models.graph import Graph

"""vr modules"""
from models.vr import VrService, VrHMD

"""mec modules"""
from models.mec import Mec 

"""migration module"""
from models.migration_ABC import Migration

"""base station modules"""
from models.base_station import BaseStation

"""other imports"""
from typing import List





class NoMigration(Migration):
    """ represents the no migration algorithm or vr services"""
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph):
        return super().check_services(base_station_set, mec_set, vr_users, graph)

    def service_migration(self, base_station_set: List[BaseStation], mec_set: List[Mec], vr_users: List[VrHMD], graph: Graph, service: VrService) -> bool:
        """ just returns False because no migration is implemented """
        return False
                '''