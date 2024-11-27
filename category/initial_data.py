from .models import StatusControl


class InitStatus:
    def __init__(self):
        init_status = [
            ("validated", "validation", "Aprobado",
                "green", "verified", True, True, False),
            ("proposed", "validation", "Propuesto",
                "blue", "lightbulb", False, True, False),
            ("need_review", "validation", "Requiere revisión",
                "pink", "dangerous", True, True, False),
            ("need_reclassify", "validation", "Requiere re-clasificación",
                "pink", "gpp_bad", True, True, False),
            ("could_reclassify", "validation", "Podría re-clasificarse",
                "orange", "gpp_maybe", True, True, False),
            ("rejected", "validation", "Rechazado",
                "red", "bug_report", False, True, False),
            ("original", "validation", "Original (v.1)",
                "light-green", "done", True, True, False),

            ("draft", "register", "Borrador",
                "blue", "edit_note", False, True, False),
            ("created", "register", "Creado",
                "green", "pending_actions", False, True, False),
            ("approved", "register", "Aprobado",
                "green", "done_all", True, True, False),
            ("need_changes", "register", "Requiere cambios",
                "orange", "new_releases", False, True, False),
            ("need_new_checking", "register", "Requiere nueva revisión",
                "pink", "report_gmailerrorred", False, True, False),
            ("discarded", "register", "Descartado",
                "red", "heart_broken", False, True, False),
            ("deleted", "register", "Eliminado",
                "red", "delete_forever", False, True, False),
            ("approved_v1", "register", "Aprobado v.1",
                "light-green", "done", True, True, False),

            ("empty", "location", "Vacío",
                "red", "location_off", False, True, False),
            ("initial", "location", "Datos iniciales",
                "blue", "edit_note", False, True, False),
            ("filled", "location", "Datos completos",
                "indigo", "edit_location", False, True, False),
            ("need_consensus", "location", "Requiere consenso",
                "pink", "report_gmailerrorred", False, True, False),
            ("finished", "location", "Finalizado",
                "green", "done_all", True, True, False),
            ("initial_v1", "location", "v1. Datos iniciales",
                "blue", "edit_note", False, True, False),
            ("need_fix", "location", "v1. Requiere corrección",
                "orange", "not_listed_location", True, True, False),
            ("migrated_v1", "location", "v1. Migrado",
                "light-green", "done", True, True, False),
        ]
        order = -1
        for data in init_status:
            name, group, public_name, color, icon, is_public, open_editor, is_deleted = data
            status, _ = StatusControl.objects.get_or_create(
                name=name
            )
            status.group = group
            status.public_name = public_name
            status.color = color
            status.icon = icon
            status.is_public = is_public
            order += 2
            if group == "register" and order < 20:
                order = 20
            if group == "location" and order < 40:
                order = 40
            status.order = order
            status.open_editor = open_editor
            status.is_deleted = is_deleted
            status.save()
