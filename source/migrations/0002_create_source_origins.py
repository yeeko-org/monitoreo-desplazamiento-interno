from django.db import migrations

from source.migrate_runpy import create_source_origins


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_source_origins),
    ]
