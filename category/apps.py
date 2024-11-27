import sys
from django.apps import AppConfig


class CategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'

    def ready(self) -> None:
        from .initial_data import InitStatus
        _ready = super().ready()
        if 'runserver' in sys.argv:
            print('Cargando datos iniciales de category...')
            InitStatus()
            print('Datos iniciales cargados.')
        return _ready
