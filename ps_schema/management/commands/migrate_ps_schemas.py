from django.core.management.base import BaseCommand
from ps_schema.initial_data import (
    InitLevels, InitCollections, InitCollectionLinks, InitFilterGroups)


class Command(BaseCommand):
    help = 'Carga de datos iniciales de ps_schema'

    def handle(self, *args, **options):
        print('Cargando datos iniciales de ps_schema')
        InitLevels()
        InitCollections()
        InitFilterGroups()
        InitCollectionLinks()
        print('Datos iniciales de ps_schema cargados')
