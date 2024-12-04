# Generated by Django 4.2.13 on 2024-12-02 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0007_remove_source_is_scrapable_source_has_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='nacional',
            field=models.CharField(blank=True, choices=[('Nal', 'Nacional'), ('Int', 'Internacional'), ('For', 'Extranjera')], max_length=3, null=True),
        ),
    ]