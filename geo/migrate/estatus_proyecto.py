from ocsa_legacy.models import EstatusProyecto
from project.models import StatusProject


class EstatusProyectoToStatusProject:
    errors: list = []

    def __init__(self):
        StatusProject.objects.all().delete()

        for estatus in EstatusProyecto.objects.all():
            if not estatus.nombre:
                continue
            try:
                status, _ = StatusProject.objects.get_or_create(
                    name=estatus.nombre
                )
                if estatus.descripcion:
                    status.description = estatus.descripcion
                    status.save()
            except Exception as e:
                self.errors.append([estatus, e])
        # self.delete_duplicates_estatus_proyectos()
