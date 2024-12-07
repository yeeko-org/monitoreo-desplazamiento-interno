from django.contrib import admin

from .models import SourceMethod, Source, SourceOrigin


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_url',)
    list_filter = ('source_origin',)


@admin.register(SourceOrigin)
class SourceOriginAdmin(admin.ModelAdmin):
    list_display = ('name', 'old_name')


@admin.register(SourceMethod)
class SourceMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'title_tag', 'subtitle_tag', 'content_tag')
