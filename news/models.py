from datetime import date
import json
from pprint import pprint
from typing import List, Optional, Any
from bs4 import BeautifulSoup
import requests

from django.db import models
from utils.open_ai import JsonRequestOpenAI
from utils.yeeko_gnews import YeekoGoogleNews

from category.models import StatusControl
from utils.date_time import get_range_dates, parse_gmt_date_list


class Source(models.Model):

    NATIONAL_CHOICES = [
        ('Nal', 'Nacional'),
        ('Int', 'Internacional'),
        ('For', 'Extranjera'),
    ]

    name = models.CharField(max_length=100)
    is_news = models.BooleanField(
        default=True, verbose_name='Es una fuente de noticias')
    main_url = models.CharField(max_length=100, blank=True, null=True)
    order = models.SmallIntegerField(default=5)
    # exclude = models.BooleanField(default=False)
    scraper_message = models.TextField(blank=True, null=True)
    # is_foreign = models.BooleanField(
    #     default=False, verbose_name='Es extranjera no internacional')
    national = models.CharField(
        choices=NATIONAL_CHOICES, max_length=3, blank=True, null=True)
    has_content = models.BooleanField(
        blank=True, null=True, verbose_name='Es scrapeable')
    is_active = models.BooleanField(
        blank=True, null=True, verbose_name='Activa')

    pre_national = models.CharField(
        choices=NATIONAL_CHOICES, max_length=3, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'


class Cluster(models.Model):
    # key_name = models.CharField(max_length=60, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Cluster'
        verbose_name_plural = 'Clusters'


class WordList(models.Model):
    cluster = models.ForeignKey(
        Cluster, on_delete=models.CASCADE, related_name='words')
    # LUCIAN: SE BORRARÁN
    main_word = models.CharField(max_length=100, unique=True)
    alternative_words = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # LUCIAN: NUEVOS CAMPOS:
    # name = models.CharField(max_length=255)
    # query_words = models.TextField(blank=True, null=True)
    # soft_query_words = models.TextField(blank=True, null=True)

    def get_all_words(self, enclose_sentences=True):
        if not self.alternative_words:
            words = [self.main_word]
        else:
            words = [self.main_word] + self.alternative_words.split(",")

        standard_words = [word.strip() for word in words]
        return [
            f'"{word}"' if " " in word and enclose_sentences else word
            for word in standard_words
        ]

    def get_or_query(self):
        return " OR ".join(self.get_all_words())

    def get_negative_query(self):
        return " ".join([f"-{word}" for word in self.get_all_words()])

    def __str__(self):
        if not self.alternative_words:
            return self.main_word

        alternative_list = self.alternative_words.split(",")
        alt_words = ", ".join(alternative_list[:2])
        if len(alternative_list) > 2:
            alt_words = alt_words + ", ..."
        return f"{self.main_word} ({alt_words})"

    class Meta:
        verbose_name = 'Lista de palabras'
        verbose_name_plural = 'Listas de palabras'
        ordering = ['cluster', 'main_word']


def words_query_union(words_query, union="OR", funtion="get_or_query"):
    if not union:
        union = " "
    else:
        union = f" {union} "
    return union.join(
        [getattr(word_list, funtion)() for word_list in words_query])


class SearchQuery(models.Model):
    name = models.CharField(max_length=100)

    query = models.TextField(blank=True, null=True)
    manual_query = models.TextField(blank=True, null=True)
    use_manual_query = models.BooleanField(default=True)

    main_words = models.ManyToManyField(
        WordList, related_name='main_queries', blank=True)
    complementary_words = models.ManyToManyField(
        WordList, related_name='complementary_queries', blank=True)
    negative_words = models.ManyToManyField(
        WordList, related_name='negative_queries', blank=True)
    # soft_negative_words = models.ManyToManyField(
    #     WordList, related_name='soft_negative_queries', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, do_words=False, **kwargs):
        print("Saving search query", do_words)
        if do_words:
            self.query_words()

        return super().save(*args, **kwargs)

    def query_words(self):
        print("Querying words")
        main_query = words_query_union(self.main_words.all())
        if not main_query:
            return

        complementary_query = words_query_union(
            self.complementary_words.all())
        negative_terms = words_query_union(
            self.negative_words.all(), union="",
            funtion="get_negative_query")

        if complementary_query or negative_terms:
            self.query = f"({main_query})"
        else:
            self.query = main_query
            return

        if complementary_query:
            self.query += f" AND ({complementary_query})"

        self.query += "{{DATE}}"

        if negative_terms:
            self.query += f" {negative_terms}"

    def search(
            self, when: Optional[Any], from_date: Optional[date],
            to_date: Optional[date]
    ):
        if self.use_manual_query:
            if not self.manual_query:
                raise ValueError("Manual query is empty")
            final_query = self.manual_query
        else:
            self.query_words()
            if not self.query:
                raise ValueError("Query is empty")
            final_query = self.query

        if when:
            links_data = self.search_when(when, final_query)
        elif from_date and to_date:
            links_data = self.search_from_to(from_date, to_date, final_query)
        else:
            raise ValueError("No dates provided")

        entries = self.search_filter_soft(
            links_data.get("entries", []))
        # if not when:
        #     entries = self.pre_clasify_openai(entries)

        return {
            "entries": entries,
            "feed": links_data.get("feed")
        }

    def search_from_to(
            self, from_date: date, to_date: date, search_query: str
    ):

        search_kwargs = {}
        range_dates = get_range_dates(None, from_date, to_date)
        all_links_data = []
        last_feed = None
        for from_date_r, to_date_r in range_dates:

            search_kwargs["from_"] = from_date_r.strftime("%Y-%m-%d")
            search_kwargs["to_"] = to_date_r.strftime("%Y-%m-%d")

            gn = YeekoGoogleNews("es", "MX")
            print("Searching...\n", search_query, "\n", search_kwargs)
            links_data = gn.search(search_query, helper=False, **search_kwargs)
            all_links_data.extend(links_data.get("entries", []))
            last_feed = links_data.get("feed", None)

        return {
            "entries": all_links_data,
            "feed": last_feed
        }

    def search_when(
            self, when: Any, search_query: str
    ):
        try:
            when = int(when)
            when = f"{when}d"
        except ValueError:
            pass
        search_kwargs = {"when": when or "1d"}
        gn = YeekoGoogleNews("es", "MX")
        print("Searching...\n", search_query, "\n", search_kwargs)
        return gn.search(search_query, helper=False, **search_kwargs)

    def search_filter_soft(self, entries: List[dict]):
        entries_filtered = []
        all_negative_words = []
        for word_list in self.negative_words.all():
            all_negative_words.extend(
                word_list.get_all_words(enclose_sentences=False))

        all_negative_words = [
            word.strip().lower() for word in all_negative_words if word.strip()]

        for entry in entries:
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            if any([
                word in title or word in summary
                for word in all_negative_words
            ]):
                continue

            entries_filtered.append(entry)
        return entries_filtered

    def pre_clasify_openai(self, entries: List[dict]):

        entries_for_openai = []
        foreign_sources = Source.objects.filter(national="For").values_list(
            "main_url", flat=True)
        for openai_entry in entries:
            title = openai_entry.get("title")
            gnews_id = openai_entry.get("id", "")
            gnews_url = openai_entry.get("link")
            gnews_source_url = openai_entry.get("source", {}).get("href")
            gnews_source_title = openai_entry.get("source", {}).get("title")
            if gnews_source_url in foreign_sources:
                continue

            note_link = NoteLink.objects.filter(gnews_url=gnews_url).first()
            if note_link:
                if note_link.is_dfi is not None or note_link.pre_is_dfi is not None:
                    continue

            entries_for_openai.append({
                "title": title,
                "id": gnews_id[:40],
                "source_url": gnews_source_url,
                "source_title": gnews_source_title
            })
        if not entries_for_openai:
            return entries

        full_prompt = json.dumps(entries_for_openai)

        pre_classify_request = JsonRequestOpenAI("news/prompt_pre_clasify.txt")
        pre_classify_response = pre_classify_request.send_prompt(full_prompt)
        if not pre_classify_response:
            return entries

        """
        title, id, source_url, source_title, is_dfi, source_is_foreign
        """
        pre_classify_data = {}
        new_foreign_sources = []
        openai_articles = pre_classify_response.get("articles", [])

        for openai_entry in openai_articles:
            if not isinstance(openai_entry, dict):
                continue

            oai_id = openai_entry.get("id")

            if not oai_id:
                continue

            gnews_source_url = openai_entry.get("source_url")
            gnews_source_is_foreign = openai_entry.get("source_is_foreign")

            # Actualización automática y/o creación de fuente?
            if gnews_source_is_foreign:
                new_foreign_sources.append(gnews_source_url)

            pre_classify_data[oai_id] = openai_entry

        if new_foreign_sources:
            new_foreign_sources = list(set(new_foreign_sources))
            Source.objects\
                .filter(main_url__in=new_foreign_sources,
                        national__isnull=True)\
                .update(pre_national="For")

        for entry in entries:
            gnews_id = entry.get("id")
            if not gnews_id:
                continue

            pre_classify_entry = pre_classify_data.get(gnews_id[:40], {})
            if pre_classify_entry:
                continue

            entry["pre_is_dfi"] = pre_classify_entry.get("is_dfi")
            entry["source"]["pre_national"] = pre_classify_entry\
                .get("source_is_foreign")

        return entries

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class ApplyQuery(models.Model):

    search_query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='apply_queries')
    created_at = models.DateTimeField(auto_now_add=True)
    # when = models.CharField(
    #     max_length=10, help_text='1d', blank=True, null=True
    # )
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)
    # LUCIAN: Nuevos campos, hay que guardarlo
    # has_errors = models.BooleanField(default=False)
    # errors = models.JSONField(blank=True, null=True)
    # last_feed = models.JSONField(blank=True, null=True)

    def search_and_save_entries(self):
        links_data = self.search_query.search(
            None, self.from_date, self.to_date)
        entries = links_data.get("entries", [])

        sources = {}
        created_count = 0
        for entry in entries:
            note_link, is_created = self.save_entry(entry, sources)
            if is_created:
                created_count += 1

        return {
            "created": created_count,
            "total": len(entries)
        }

    def save_entry(self, entry: dict, sources: dict):
        source_name = entry.get("source", {}).get("title")
        if source_name not in sources:
            source_url = entry.get("source", {}).get("href")
            source, _ = Source.objects.get_or_create(
                name=source_name,
                defaults={"main_url": source_url}
            )
            sources[source_name] = source
        else:
            source = sources[source_name]

        note_link, is_created = NoteLink.objects.get_or_create(
            gnews_url=entry.get("link"),
            defaults=dict(
                title=entry.get("title"),
                description=entry.get("summary"),
                source=source,
                published_at=parse_gmt_date_list(
                    entry.get("published_parsed"))
            )
        )
        note_link.queries.add(self)
        return note_link, is_created

    def __str__(self):
        return self.search_query.name

    class Meta:
        verbose_name = 'Aplicación de consulta'
        verbose_name_plural = 'Aplicaciones de consulta'


class NoteLink(models.Model):
    gnews_url = models.URLField(max_length=800, unique=True)
    real_url = models.URLField(max_length=800, blank=True, null=True)
    title = models.CharField(max_length=200)
    # description = models.TextField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='note_links')
    published_at = models.DateTimeField(blank=True, null=True)
    queries = models.ManyToManyField(
        ApplyQuery, related_name='note_links', blank=True)
    gnews_entry = models.JSONField(blank=True, null=True)
    is_dfi = models.BooleanField(blank=True, null=True)
    pre_is_dfi = models.BooleanField(blank=True, null=True)

    notes: models.QuerySet["NoteContent"]

    def __str__(self):
        return self.gnews_url[:30]

    def get_response(self):
        response = requests.get(self.real_url or self.gnews_url)
        if response.status_code == 200:
            if not self.real_url:
                self.real_url = response.url
                self.save()
            return response

    def get_content(self):
        response = self.get_response()
        if response:
            response.encoding = 'utf-8'
        return response.content if response else None

    def get_content_text(self):
        response = self.get_response()
        if not response:
            return ""
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator="\n")


class SourceMethod(models.Model):

    name = models.CharField(max_length=200)

    title_tag = models.CharField(
        max_length=200, blank=True, null=True)
    subtitle_tag = models.CharField(
        max_length=200, blank=True, null=True)
    content_tag = models.TextField(blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)

    # validated = models.BooleanField(default=False)
    # sources = models.ManyToManyField(
    #     Source, related_name='methods', blank=True)
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='methods')

    # def _valid_source(self, source: Source):
    #     return self.sources.filter(pk=source.pk).exists()

    def content_by_link(self, note_link: NoteLink):
        from bs4 import BeautifulSoup
        link_content = note_link.get_content()
        if not link_content:
            return None
        soup = BeautifulSoup(link_content, 'html.parser')

        def get_text(tag, soup):
            tag_type = "class"
            if "=" in tag:
                tag_type = tag.split(":")[0]
                tag = tag.split(":")[1]
                tag = tag.replace('"', '').replace("'", "")

            if "id" in tag_type:
                find_kwargs = {"id": tag}
            else:
                find_kwargs = {"class_": tag}
            tags = soup.find_all(**find_kwargs)

            return " ".join([t.get_text(strip=True) for t in tags])

        title = get_text(self.title_tag, soup)
        subtitle = get_text(self.subtitle_tag, soup)
        content = get_text(self.content_tag, soup)

        return NoteContent.objects.create(
            note_link=note_link,
            title=title,
            subtitle=subtitle,
            content=content,
            source_method=self,
            source=note_link.source
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Método de fuente'
        verbose_name_plural = 'Métodos de fuente'


class NoteContent(models.Model):
    # Todo FUTURO: quitar:
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE,
        verbose_name='Fuente de información')
    note_link = models.ForeignKey(
        NoteLink, on_delete=models.CASCADE, related_name='note_contents')
    source_method = models.ForeignKey(
        SourceMethod, on_delete=models.CASCADE, related_name='note_contents',
        null=True, blank=True)

    # title = models.CharField(max_length=255)
    # Todo FUTURO: quitar:
    title = models.TextField(blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(
        max_length=255, blank=True, null=True)
    section = models.CharField(max_length=120, blank=True, null=True)
    pages = models.CharField(max_length=80, blank=True, null=True)

    content = models.TextField(blank=True, null=True)
    content_full = models.TextField(blank=True, null=True)

    full_html = models.TextField(blank=True, null=True)
    full_text = models.TextField(blank=True, null=True)

    structured_content = models.JSONField(blank=True, null=True)

    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # link_content_text = models.TextField(blank=True, null=True)

    files: models.QuerySet["NoteFile"]
    status_register_id = str | None

    def __str__(self):
        return self.title or self.link.title

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


def upload_to_note_file(instance, filename):
    return f'note_file/{instance.note.pk}/{filename}'


class NoteFile(models.Model):
    note = models.ForeignKey(
        NoteContent, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_to_note_file, max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name if self.file else 'Archivo sin nombre'

    class Meta:
        verbose_name = 'Archivo de nota'
        verbose_name_plural = 'Archivos de nota'
