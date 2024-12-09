
def add_is_internal_dis(apps, schema_editor):
    NoteLink = apps.get_model('news', 'NoteLink')
    is_dfi = NoteLink.objects.filter(is_dfi=True)
    is_dfi.update(is_internal_dis='valid')
    is_not_dfi = NoteLink.objects.filter(is_dfi=False)
    is_not_dfi.update(is_internal_dis='invalid')


def create_source_origins(apps, schema_editor):
    NATIONAL_CHOICES = [
        (None, 'Desconocido', 'blue-grey', False),
        ('Nal', 'Nacional', 'success', True),
        ('Int', 'Internacional', 'primary', True),
        ('For', 'Extranjera', 'pink', False),
    ]
    SourceOrigin = apps.get_model('news', 'SourceOrigin')
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
    Source = apps.get_model('news', 'Source')
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


def first_valid_options(apps, schema_editor):
    ValidOption = apps.get_model('news', 'ValidOption')
    init_valid_options = [
        ('unknown', 'No estoy seguro', 'help', 'lime'),
        ('valid', 'Es válido', 'check', 'success'),
        ('invalid', 'No es válido', 'close', 'error'),
    ]
    order = 1
    for value, name, icon, color in init_valid_options:
        valid_option, _ = ValidOption.objects.get_or_create(
            name=name,
            defaults={
                'description': '',
                'icon': icon,
                'color': color,
                'order': order,
            }
        )
        valid_option.icon = icon
        valid_option.color = color
        valid_option.order = order
        valid_option.save()
        order += 1


def move_dis_to_valid_option(apps, schema_editor):
    NoteLink = apps.get_model('news', 'NoteLink')
    ValidOption = apps.get_model('news', 'ValidOption')
    equivalences = [
        ('valid', 'Válido', 'Es válido'),
        ('invalid', 'Inválido', 'No es válido'),
        ('unknown', 'Podría ser', 'No estoy seguro'),
    ]
    for old_name, new_name, saved_name in equivalences:
        valid_options = ValidOption.objects.filter(name=saved_name)
        print(f"Moving {old_name} to {new_name}")
        print(valid_options)
        valid_options.update(name=new_name)
        valid_option = ValidOption.objects.filter(name=new_name).first()
        if valid_option:
            NoteLink.objects\
                .filter(is_internal_dis=old_name)\
                .update(valid_option=valid_option)
        else:
            print(f"Error: {new_name} not found")
