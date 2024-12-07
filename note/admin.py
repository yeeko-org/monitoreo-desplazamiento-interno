from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path

from .models import NoteLink, NoteContent
from source.models import SourceMethod


def apply_selected_method(modeladmin, request, queryset):
    if 'apply' in request.POST:
        selected_method_id = request.POST['source_method']
        selected_method = SourceMethod.objects.get(id=selected_method_id)

        for note_link in queryset:
            selected_method.content_by_link(note_link)
            print(f'Aplicando {selected_method} a {note_link}')

        modeladmin.message_user(request, "Método aplicado exitosamente")
        return redirect(request.get_full_path())

    print("SourceMethod.objects.all()", SourceMethod.objects.all().count())

    return render(request, 'admin/apply_selected_method.html', context={

        'note_links': queryset,
        'source_methods': SourceMethod.objects.all(),
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    })


apply_selected_method.short_description = "Scrapear con método seleccionado"  # type: ignore


class NoteInline(admin.StackedInline):
    model = NoteContent
    extra = 0
    fields = ('title', 'subtitle', 'content', "source_method")
    readonly_fields = ('title', 'subtitle', 'content', "source_method")


@admin.register(NoteLink)
class NoteLinkAdmin(admin.ModelAdmin):
    actions = [apply_selected_method]
    list_display = ('url_display', 'title', 'source', "note_links_count")
    list_filter = ("source__source_origin", 'source',)
    search_fields = ('title', 'source')
    inlines = [NoteInline]

    def url_display(self, obj: NoteLink):
        url = obj.real_url or obj.gnews_url
        return url[:50]

    def note_links_count(self, obj: NoteLink):
        return obj.note_contents.count()

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('apply-selected-method/',
                 self.admin_site.admin_view(apply_selected_method))
        ]
        return custom_urls + urls

    def apply_selected_method_view(self, request):
        if request.method == 'POST':
            selected = request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)
            queryset = NoteLink.objects.filter(pk__in=selected)
            return apply_selected_method(self, request, queryset)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@admin.register(NoteContent)
class NoteContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'content')
    raw_id_fields = ('note_link', 'source_method')
