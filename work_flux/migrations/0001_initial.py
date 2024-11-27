# Generated by Django 4.2.9 on 2024-11-26 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StatusControl',
            fields=[
                ('name', models.CharField(max_length=120, primary_key=True, serialize=False)),
                ('group', models.CharField(choices=[('register', 'Registro'), ('validation', 'Validación'), ('location', 'Ubicación')], default='petition', max_length=10, verbose_name='grupo de status')),
                ('public_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('color', models.CharField(blank=True, help_text='https://vuetifyjs.com/en/styles/colors/', max_length=30, null=True)),
                ('icon', models.CharField(blank=True, max_length=40, null=True)),
                ('order', models.IntegerField(default=4)),
                ('is_public', models.BooleanField(default=True)),
                ('open_editor', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Status de control',
                'verbose_name_plural': 'Status de control (TODOS)',
                'ordering': ['group', 'order'],
            },
        ),
    ]
