# Generated by Django 4.2.13 on 2024-12-12 22:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0006_remove_notelink_pre_is_dfi'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notelink',
            name='is_dfi',
        ),
    ]