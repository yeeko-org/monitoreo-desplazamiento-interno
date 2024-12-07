def create_source_origins(apps, schema_editor):
    NATIONAL_CHOICES = [
        (None, 'Desconocido', 'blue-grey', False),
        ('Nal', 'Nacional', 'success', True),
        ('Int', 'Internacional', 'primary', True),
        ('For', 'Extranjera', 'pink', False),
    ]
    SourceOrigin = apps.get_model('source', 'SourceOrigin')
    for order, (old_name, name, color, in_scope) in enumerate(NATIONAL_CHOICES):
        SourceOrigin.objects.get_or_create(
            name=name,
            old_name=old_name,
            defaults=dict(
                color=color,
                order=order,
                # in_scope=in_scope
            )
        )
    Source = apps.get_model('source', 'Source')
    for source_origin in SourceOrigin.objects.all():
        Source.objects\
            .filter(national=source_origin.old_name)\
            .update(source_origin=source_origin)
        Source.objects\
            .filter(pre_national=source_origin.old_name)\
            .update(pre_source_origin=source_origin)
    empty_source_origin = SourceOrigin.objects.get(name='Desconocido')
    Source.objects\
        .filter(national__isnull=True)\
        .update(source_origin=empty_source_origin)
