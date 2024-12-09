# Generated by Django 4.2.13 on 2024-12-07 03:15

from django.db import migrations, models
import django.db.models.deletion


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


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0030_validoption'),
    ]

    operations = [
        migrations.AddField(
            model_name='notelink',
            name='valid_option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.validoption'),
        ),
        migrations.AddField(
            model_name='validoption',
            name='color',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='validoption',
            name='icon',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.RunPython(first_valid_options),
        migrations.RunPython(move_dis_to_valid_option),

    ]
