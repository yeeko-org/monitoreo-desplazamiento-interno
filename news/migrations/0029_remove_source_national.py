# Generated by Django 4.2.13 on 2024-12-07 02:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0028_alter_source_options_remove_source_is_news_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='national',
        ),
    ]
