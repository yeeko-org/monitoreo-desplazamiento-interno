from django.db import models
from category.models import StatusControl
# from project.models import Project
# from event.models import Event


def default_alternative_names():
    return []


# Para todos los casos de comparación por name, estandariza con text_normalizer
# Para estados vas a utilizar la lista de initial_data y vas a tomar las
# alternative_names del campo other_names, separados por comas.
class State(models.Model):
    inegi_code = models.CharField(max_length=2, verbose_name="Clave INEGI")
    name = models.CharField(max_length=50, verbose_name="Nombre")
    short_name = models.CharField(
        max_length=20, verbose_name="Nombre Corto",
        blank=True, null=True)
    code_name = models.CharField(
        max_length=6, verbose_name="Nombre Clave",
        blank=True, null=True)
    alternative_names = models.JSONField(
        default=default_alternative_names,
        verbose_name="Lista nombres alternativos",
        help_text="Ocupar para OCAMIS",
    )

    def __str__(self):
        return self.short_name or self.code_name or self.name

    class Meta:
        ordering = ["inegi_code"]
        verbose_name = "Entidad Federativa"
        verbose_name_plural = "Entidades Federativas"


# Para municipios vamos a tomar el archivo municipios.csv y vas a tomar las
# siguientes columnas:
# CVE_ENT --> Municipality.state.inegi_code
# CVE_MUN --> Municipality.inegi_code
# NOM_MUN --> Municipality.name
# std_name lo construyes con text_normalizer(NOM_MUN)
# POB_TOTAL --> Municipality.population
# complete_code genéralo con la concatenación de Cve_Ent y Cve_Mun,
# en medio de ellos un guión, ejemplo: 01-001

class Municipality(models.Model):

    inegi_code = models.CharField(max_length=6, verbose_name="Clave INEGI")
    complete_code = models.CharField(
        max_length=8, verbose_name="Clave INEGI Completa")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    std_name = models.CharField(
        max_length=255, verbose_name="Nombre Estandarizado")
    state = models.ForeignKey(
        State, verbose_name="State",
        null=True, on_delete=models.CASCADE,
        related_name="municipalities")
    population = models.IntegerField(
        blank=True, null=True, verbose_name="Población")
    latitude = models.FloatField(
        blank=True, null=True, verbose_name="Latitud de cabecera")
    longitude = models.FloatField(
        blank=True, null=True, verbose_name="Longitud de cabecera")
    altitude = models.IntegerField(
        blank=True, null=True, verbose_name="Altitud de cabecera")

    def __str__(self):
        return "%s - %s" % (self.name, self.state)

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ["inegi_code"]


# Para localidad, hay un archivo de .txt y un archivo de .csv, con el que sea
# más sencillo, con ese, vas a tomar las siguientes columnas:
# CVE_ENT --> Locality.municipality.state.inegi_code
# CVE_MUN --> Locality.municipality.inegi_code
# CVE_LOC --> Locality.inegi_code
# NOM_LOC --> Locality.name
# POB_TOTAL --> Locality.population
# LAT_DECIMAL --> Locality.latitude
# LON_DECIMAL --> Locality.longitude
# ALTITUD --> Locality.altitude
# complete_code genéralo con la concatenación de municipality.complete_code y
# inegi_code, en medio de ellos un guión.
# Ejemplo: 01-001-0001

class Locality(models.Model):
    inegi_code = models.CharField(max_length=6, verbose_name="Clave INEGI")
    complete_code = models.CharField(
        max_length=12, verbose_name="Clave INEGI Completa")
    name = models.CharField(max_length=120, verbose_name="Nombre")
    municipality = models.ForeignKey(
        Municipality, verbose_name="Municipality",
        null=True, on_delete=models.CASCADE,
        related_name="localities")
    population = models.IntegerField(
        blank=True, null=True, verbose_name="Población")
    is_rural = models.BooleanField(default=False, verbose_name="Es rural")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    altitude = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.municipality)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"


class Location(models.Model):
    # project = models.ForeignKey(
    #     Project, on_delete=models.CASCADE, blank=True, null=True,
    #     related_name="locations")
    # event = models.ForeignKey(
    #     Event, on_delete=models.CASCADE, blank=True, null=True,
    #     related_name="locations")
    state = models.ForeignKey(
        State, on_delete=models.CASCADE,
        related_name="locations", blank=True, null=True)
    municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE,
        related_name="locations", blank=True, null=True)
    locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE,
        related_name="locations", blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geojson = models.JSONField(blank=True, null=True)
    ubicacion_id_ref = models.IntegerField(blank=True, null=True)
    status_location = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return f"{self.state or 'sin entidad'} - {self.details}"

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
