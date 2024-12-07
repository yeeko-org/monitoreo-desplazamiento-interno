from django.contrib import admin, messages

from search.models import ApplyQuery, SearchQuery, WordList


@admin.register(WordList)
class WordListAdmin(admin.ModelAdmin):
    list_display = ('name', 'cluster')


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
            f"resultados, se crearon {results['created']} Note Links")
