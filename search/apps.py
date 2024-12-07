import sys
from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'

    def ready(self) -> None:
        from .initial_data import InitClusters
        _ready = super().ready()
        if 'runserver' in sys.argv:
            print('Cargando datos iniciales de clusters...')
            InitClusters()
            print('Datos iniciales cargados.')
        return _ready
