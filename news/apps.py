import sys
from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self) -> None:
        from .initial_data import InitClusters
        _ready = super().ready()
        if 'runserver' in sys.argv:
            print('Cargando datos iniciales de clusters...')
            InitClusters()
            print('Datos iniciales cargados.')
        return _ready
