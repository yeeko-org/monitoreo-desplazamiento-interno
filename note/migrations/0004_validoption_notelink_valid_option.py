# Generated by Django 4.2.13 on 2024-12-09 02:26

from django.db import migrations, models
import django.db.models.deletion


def first_valid_options(apps, schema_editor):
    ValidOption = apps.get_model('note', 'ValidOption')
    init_valid_options = [
        ('valid', 'Válido', 'check', 'success'),
        ('invalid', 'Inválido', 'close', 'error'),
        ('unknown', 'Podría ser', 'help', 'lime'),
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
        # valid_option.save()
        order += 1


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0003_add_is_internal_dis'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValidOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('order', models.SmallIntegerField(default=5)),
                ('icon', models.CharField(blank=True, max_length=100, null=True)),
                ('color', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Opción de validación',
                'verbose_name_plural': 'Opciones de validación',
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='notelink',
            name='valid_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='note.validoption'),
        ),
        migrations.RunPython(first_valid_options),
    ]
