from django.core.management.base import BaseCommand

from geo.migrate.ubicacio import UbicacionesToLocations


class Command(BaseCommand):
    help = 'Migrate Ubicaciones'

    def handle(self, *args, **options):
        print("Migrating Ubicaciones")
        migrate_ubicaciones = UbicacionesToLocations()

        for error in migrate_ubicaciones.errors:
            print(error)
