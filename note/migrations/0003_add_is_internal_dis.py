from django.db import migrations

from note.migrate_runpy import add_is_internal_dis


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(add_is_internal_dis),
    ]
