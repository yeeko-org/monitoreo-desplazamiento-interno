import json
from typing import Dict, Tuple
from actor.migrate.common import text_normalizer
from ocsa_legacy.models import Ubicacion
from geo.models import Locality, Location, Municipality, State


class UbicacionesToLocations:
    states: Dict[str, int] = {}
    errors = []

    def __init__(self):
        self.load_states()
        for ubicacion in Ubicacion.objects.all():
            fields = [
                "estado", "municipio", "localidad", "latitud", "longitud",
                "geom", "especificaciones"]
            if ubicacion.tipo_ubicacion == "punto":
                for field in fields:
                    if value := getattr(ubicacion, field):
                        if value != "SD":
                            break
                else:
                    continue
            try:
                self.migrate_ubicacion(ubicacion)
            except Exception as e:
                self.errors.append([ubicacion, e])

    def load_states(self):
        for state in State.objects.all():
            self.states[text_normalizer(state.short_name.lower())] = state.pk

            for alt_name in state.alternative_names:
                self.states[text_normalizer(alt_name.lower())] = state.pk

    def get_state_id(self, state_name: str | None) -> int | None:
        if not state_name:
            return None
        return self.states.get(text_normalizer(state_name.lower()), None)

    def get_municipality(
        self, state_id: int | None,
        municipality_name: str | None
    ) -> Tuple[Municipality | None, int]:

        if not municipality_name:
            return None, 0

        std_name = text_normalizer(municipality_name)

        municipality_query = Municipality.objects.filter(
            state_id=state_id, std_name=std_name)
        municipality_count = municipality_query.count()

        if not municipality_count:
            return None, municipality_count

        return municipality_query.first(), municipality_count

    def get_locality(
        self, municipality: Municipality | None,
        locality_name: str | None
    ) -> Tuple[Locality | None, int]:

        if not locality_name or not municipality:
            return None, 0

        locality_query = Locality.objects.filter(
            municipality=municipality, name__iexact=locality_name)
        locality_count = locality_query.count()

        if not locality_count:
            return None, locality_count

        return locality_query.first(), locality_count

    def migrate_ubicacion(self, ubicacion: Ubicacion):
        details = f"{ubicacion.especificaciones}\n\r" \
            if ubicacion.especificaciones else ""
        comments = []

        if ubicacion.tipo_ubicacion != "punto":
            # comments.append(f"Tipo de ubicación: {ubicacion.tipo_ubicacion}")
            details += f"Tipo de ubicación: {ubicacion.tipo_ubicacion}\n\r"

        state_id = self.get_state_id(ubicacion.estado)
        if not state_id and ubicacion.estado:
            comments.append(f"Estado no encontrado: {ubicacion.estado}")

        municipality, municipality_count = self.get_municipality(
            state_id, ubicacion.municipio)
        if not municipality and ubicacion.municipio:
            comments.append(f"Municipio no encontrado: {ubicacion.municipio}")
        if municipality_count > 1:
            comments.append(
                f"Se encontraron {municipality_count} municipios con el mismo "
                f"nombre{ubicacion.municipio}")

        locality, locality_count = self.get_locality(
            municipality, ubicacion.localidad)
        if not locality and ubicacion.localidad:
            comments.append(f"Localidad no encontrada: {ubicacion.localidad}")
        if locality_count > 1:
            comments.append(
                f"Se encontraron {locality_count} localidades con el mismo "
                f"nombre{ubicacion.localidad}")

        # details = (ubicacion.especificaciones or "") + "\n\r" + details

        geojson = None
        try:
            geojson = json.loads(ubicacion.geom) if ubicacion.geom else None
        except json.JSONDecodeError:
            comments.append(
                "Error al parsear el geojson. El campo se guardará como nulo")
            details += f"geom: {ubicacion.geom}\n\r"
        details = details.strip()
        status_location = 'initial_v1'
        final_comments = None
        if comments:
            final_comments = "; ".join(comments)
            final_comments = f"YEEKO: {final_comments}"
            status_location = 'need_fix'
        elif geojson or ubicacion.latitud or ubicacion.longitud:
            status_location = 'migrated_v1'

        Location.objects.create(
            state_id=state_id,
            municipality=municipality,
            locality=locality,
            details=details,
            latitude=ubicacion.latitud,
            longitude=ubicacion.longitud,
            geojson=geojson,
            ubicacion_id_ref=ubicacion.pk,
            comments=final_comments,
            status_location_id=status_location
        )
