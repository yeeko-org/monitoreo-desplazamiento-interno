# Generated by Django 4.2.13 on 2024-11-29 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_alter_cluster_options_alter_link_real_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='subtitle',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
