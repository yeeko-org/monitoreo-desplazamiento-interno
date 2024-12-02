# Generated by Django 4.2.13 on 2024-12-01 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_alter_sourcemethod_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='link',
            old_name='valid',
            new_name='is_dfi',
        ),
        migrations.AlterField(
            model_name='applyquery',
            name='search_query',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applied', to='news.searchquery'),
        ),
    ]
