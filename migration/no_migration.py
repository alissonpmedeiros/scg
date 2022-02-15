from migration.migration import Migration
from vr import VrService

class NoMigration(Migration):

    def get_migrations(self):
        return super().get_migrations()
    
    def check_services(self, base_station_set: list, mec_set: list, vr_users: list):
        return super().check_services(base_station_set, mec_set, vr_users)

    def service_migration(self, base_station_set: list, mec_set: list, vr_users: list, service: VrService):
        return super().service_migration(base_station_set, mec_set, vr_users, service)