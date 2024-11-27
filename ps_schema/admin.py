from django.contrib import admin
from django.contrib.admin import register
from ps_schema.models import Level, Collection, CollectionLink, FilterGroup


@register(Level)
class PsSchemaAdmin(admin.ModelAdmin):
    list_display = ('key_name', 'name', 'order')
    list_editable = ('order',)


class CollectionLinkInline(admin.TabularInline):
    model = CollectionLink
    fk_name = 'parent'
    extra = 0


class CollectionLinkChildInline(admin.TabularInline):
    model = CollectionLink
    fk_name = 'child'
    extra = 0


@register(CollectionLink)
class CollectionLinkAdmin(admin.ModelAdmin):
    list_display = ('parent', 'child', 'link_type', 'is_multiple', 'is_provisional', 'is_mandatory')
    list_filter = (
        'link_type', 'is_multiple', 'is_provisional', 'is_mandatory',
        'parent__app_label', 'child__app_label')
    search_fields = ('parent__snake_name', 'child__snake_name')


@register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'model_name', 'level', 'app_label', 'order',
        'link_list_display')
    list_editable = ('order',)
    list_filter = ('level', 'app_label')
    inlines = [CollectionLinkInline, CollectionLinkChildInline]

    def link_list_display(self, obj):
        from django.utils.html import format_html
        # senders = UserMessenger.objects.filter(user=obj)
        app_label = obj._meta.app_label

        def build_list(links, target_name):
            html_list = ''
            space = "&nbsp;" * 3
            for link in links:
                target = getattr(link, target_name)
                html_list = html_list + (
                    f'<a href="/admin/{app_label}/collection'
                    f'/{target.snake_name}/change/" target="_blank">'
                    f'● {target} <br>{space}({target.level.key_name})</a><br>')
            return html_list

        html_list = ''
        if parent_links := obj.parent_links.all():
            html_list += f'<b>Parent Links:</b><br>{build_list(parent_links, "parent")}'
        if child_links := obj.child_links.all():
            html_list += f'<b>Child Links:</b><br>{build_list(child_links, "child")}'
        # model._meta.app_label
        return format_html(html_list)


@register(FilterGroup)
class FilterGroupAdmin(admin.ModelAdmin):
    list_display = (
        'key_name', 'name', 'main_collection', 'order')
    list_editable = ('order',)
