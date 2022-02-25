from vr.vr import VrService
from mec.mec import MecAgent
from migration.migration_ABC import Migration

class NoMigration(Migration):
    """ represents the no migration algorithm or vr services"""
    
    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(self, base_station_set: list, mec_set: list, vr_users: list):
        return super().check_services(base_station_set, mec_set, vr_users)

    def service_migration(self, base_station_set: list, mec_set: list, vr_users: list, service: VrService) -> bool:
        """_summary_
        
        just returns False because no migration is implemented
        """
        
        return False
                