def add_is_internal_dis(apps, schema_editor):
    NoteLink = apps.get_model('note', 'NoteLink')
    is_dfi = NoteLink.objects.filter(is_dfi=True)
    is_dfi.update(is_internal_dis='valid')
    is_not_dfi = NoteLink.objects.filter(is_dfi=False)
    is_not_dfi.update(is_internal_dis='invalid')
