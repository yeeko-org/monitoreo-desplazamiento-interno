from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import path

from .models import (
    Link, Note, SearchQuery, ApplyQuery, SourceMethod, Source,  WordList)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_news', 'main_url', 'order')
    list_editable = ('order',)


@admin.register(WordList)
class WordListAdmin(admin.ModelAdmin):
    list_display = ('main_word', 'cluster')


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query',)
    filter_horizontal = (
        'main_words', 'complementary_words', 'negative_words')

    def save_model(self, request, obj, form, change):
        obj.save(do_words=False)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.save(do_words=True)
        


@admin.register(ApplyQuery)
class ApplyQueryAdmin(admin.ModelAdmin):
    list_display = ('search_query', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('search_query__name',)

    def save_model(self, request, obj: ApplyQuery, form, change):
        obj.save()
        results = obj.search_and_save_entries()
        messages.success(
            request, f"Se encontraron {results['total']} "
            f"resultados, se crearon {results['created']} links")


def apply_selected_method(modeladmin, request, queryset):
    if 'apply' in request.POST:
        selected_method_id = request.POST['source_method']
        selected_method = SourceMethod.objects.get(id=selected_method_id)

        for link in queryset:
            selected_method.note_by_link(link)
            print(f'Aplicando {selected_method} a {link}')

        modeladmin.message_user(request, "Método aplicado exitosamente")
        return redirect(request.get_full_path())

    print("SourceMethod.objects.all()", SourceMethod.objects.all().count())

    return render(request, 'admin/apply_selected_method.html', context={

        'links': queryset,
        'source_methods': SourceMethod.objects.all(),
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
    })


apply_selected_method.short_description = "Scrapear con método seleccionado"  # type: ignore


class NoteInline(admin.StackedInline):
    model = Note
    extra = 0
    fields = ('title', 'subtitle', 'content', "source_method")
    readonly_fields = ('title', 'subtitle', 'content', "source_method")


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    actions = [apply_selected_method]
    list_display = ('url_display', 'title', 'source', "notes_count")
    list_filter = ('source',)
    search_fields = ('title', 'source')
    inlines = [NoteInline]

    def url_display(self, obj: Link):
        url = obj.real_url or obj.gnews_url
        return url[:50]

    def notes_count(self, obj: Link):
        return obj.notes.count()

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
            queryset = Link.objects.filter(pk__in=selected)
            return apply_selected_method(self, request, queryset)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@admin.register(SourceMethod)
class SourceMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'title_tag', 'subtitle_tag', 'content_tag')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'content')
    raw_id_fields = ('link', 'source_method')
