# Generated by Django 4.2.13 on 2024-07-10 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gnews_url', models.URLField(max_length=800)),
                ('real_url', models.URLField(blank=True, null=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('source', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.TextField()),
                ('when', models.CharField(default='1d', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SourceMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=200)),
                ('title_tag', models.CharField(max_length=200)),
                ('subtitle_tag', models.CharField(max_length=200)),
                ('content_tag', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news', to='news.link')),
                ('source_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='news', to='news.sourcemethod')),
            ],
        ),
        migrations.AddField(
            model_name='link',
            name='query',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='news.searchquery'),
        ),
    ]
