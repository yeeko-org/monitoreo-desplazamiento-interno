from django.contrib import admin
from geo.models import Locality, Municipality, State, Location


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'municipality_id', 'population',
                    'latitude', 'longitude', 'altitude')
    raw_id_fields = ('municipality',)


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state_id', 'population')
    raw_id_fields = ('state',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'inegi_code')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('state', 'municipality', 'locality', 'details',
                    'latitude', 'longitude')
    raw_id_fields = ('state', 'municipality', 'locality')
