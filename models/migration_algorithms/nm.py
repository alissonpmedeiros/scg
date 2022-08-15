
import typing
if typing.TYPE_CHECKING:
    """ model modules"""
    from models.mec import Mec 
    from models.vr import VrHMD 
    from models.graph import Graph 
    from models.vr import VrService 
    from models.base_station import BaseStation 
    
from models.migration_ABC import Migration

"""other modules"""
from typing import Dict


class NoMigration(Migration):
    """ represents the no migration algorithm or vr services"""
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph'
    ) -> None:
        return super().check_services(
            base_station_set, mec_set, hmds_set, graph
        )

    def service_migration(
        self, 
        base_station_set: Dict[str,'BaseStation'], 
        mec_set: Dict[str,'Mec'], 
        hmds_set: Dict[str,'VrHMD'], 
        graph: 'Graph', 
        service: 'VrService'
    ) -> bool:
        """ just returns False because no migration is implemented """
        self.unsuccessful_migrations += 1
        return False
                