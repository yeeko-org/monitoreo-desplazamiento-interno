# Generated by Django 4.2.13 on 2024-12-01 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_rename_querys_link_queries_remove_link_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sourcemethod',
            options={'verbose_name': 'Método de fuente', 'verbose_name_plural': 'Métodos de fuente'},
        ),
        migrations.RenameField(
            model_name='note',
            old_name='link_content_text',
            new_name='full_text',
        ),
        migrations.RemoveField(
            model_name='sourcemethod',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='sourcemethod',
            name='validated',
        ),
        migrations.AddField(
            model_name='note',
            name='content_full',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='note',
            name='full_html',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sourcemethod',
            name='source',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='methods', to='news.source'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sourcemethod',
            name='tags',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='subtitle',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='sourcemethod',
            name='content_tag',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sourcemethod',
            name='subtitle_tag',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='sourcemethod',
            name='title_tag',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]