from datetime import date, datetime
from typing import Optional
from bs4 import BeautifulSoup
import requests

from django.db import models
from pygooglenews import GoogleNews

from category.models import StatusControl
from utils.date_time import parse_gmt_date_list


class Source(models.Model):
    name = models.CharField(max_length=100)
    is_news = models.BooleanField(
        default=True, verbose_name='Es una fuente de noticias')
    main_url = models.CharField(max_length=100, blank=True, null=True)
    order = models.SmallIntegerField(default=5)
    exclude = models.BooleanField(default=False)

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
        Cluster, on_delete=models.CASCADE, related_name='words',
        blank=True, null=True)
    main_word = models.CharField(max_length=100, unique=True)
    alternative_words = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        if not self.alternative_words:
            return self.main_word

        alternative_list = self.alternative_words.split(",")
        alt_words = ", ".join(alternative_list[:2])
        if len(alternative_list) > 2:
            alt_words = alt_words + ", ..."
        return f"{self.main_word} ({alt_words})"

    def get_all_words(self):
        if not self.alternative_words:
            words = [self.main_word]
        else:
            words = [self.main_word] + self.alternative_words.split(",")

        standard_words = [word.strip() for word in words]
        return [
            f'"{word}"' if " " in word else word
            for word in standard_words
        ]

    def get_or_query(self):
        return " OR ".join(self.get_all_words())

    def get_negative_query(self):
        return " ".join([f"-{word}" for word in self.get_all_words()])


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

        if negative_terms:
            self.query += f" {negative_terms}"

    def search(
            self, when: Optional[str], from_date: Optional[date],
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

        search_kwargs = {}
        if from_date and to_date:
            search_kwargs["from_"] = from_date.strftime("%Y-%m-%d")
            search_kwargs["to_"] = to_date.strftime("%Y-%m-%d")
        else:
            search_kwargs = {"when": when or "1d"}
        gn = GoogleNews("es", "MX")
        notes = gn.search(final_query, helper=True, **search_kwargs)
        return notes.get("entries", [])

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class ApplyQuery(models.Model):

    search_query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='applys')
    created_at = models.DateTimeField(auto_now_add=True)
    when = models.CharField(
        max_length=10, help_text='1d', blank=True, null=True
    )
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    def search_and_save_entries(self):
        entries = self.search_query.search(
            self.when, self.from_date, self.to_date)

        sources = {}
        created_count = 0
        for entry in entries:
            link, is_created = self.save_entry(entry, sources)
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

        link, is_created = Link.objects.get_or_create(
            gnews_url=entry.get("link"),
            defaults=dict(
                title=entry.get("title"),
                description=entry.get("summary"),
                source=source,
                published_at=parse_gmt_date_list(
                    entry.get("published_parsed"))
            )
        )
        link.querys.add(self)
        return link, is_created

    def __str__(self):
        return self.search_query.name

    class Meta:
        verbose_name = 'Aplicación de consulta'
        verbose_name_plural = 'Aplicaciones de consulta'


class Link(models.Model):
    gnews_url = models.URLField(max_length=800, unique=True)
    real_url = models.URLField(max_length=800, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='links')
    published_at = models.DateTimeField(blank=True, null=True)
    querys = models.ManyToManyField(
        ApplyQuery, related_name='links', blank=True)
    valid = models.BooleanField(blank=True, null=True)

    notes: models.QuerySet["Note"]

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

    title_tag = models.CharField(max_length=200)
    subtitle_tag = models.CharField(max_length=200)
    content_tag = models.TextField()

    validated = models.BooleanField(default=False)
    sources = models.ManyToManyField(
        Source, related_name='methods', blank=True)

    def _valid_source(self, source: Source):
        return self.sources.filter(pk=source.pk).exists()

    def __str__(self):
        return self.name

    def note_by_link(self, link: Link):
        from bs4 import BeautifulSoup
        link_content = link.get_content()
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

        return Note.objects.create(
            link=link,
            title=title,
            subtitle=subtitle,
            content=content,
            source_method=self,
            source=link.source
        )


class Note(models.Model):
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE,
        verbose_name='Fuente de información')
    link = models.ForeignKey(
        Link, on_delete=models.CASCADE, related_name='notes')
    source_method = models.ForeignKey(
        SourceMethod, on_delete=models.CASCADE, related_name='notes',
        null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    section = models.CharField(max_length=120, blank=True, null=True)
    pages = models.CharField(max_length=80, blank=True, null=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    structured_content = models.JSONField(blank=True, null=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    link_content_text = models.TextField(blank=True, null=True)

    files: models.QuerySet["NoteFile"]
    status_register_id = str | None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


def upload_to_note_file(instance, filename):
    return f'note_file/{instance.note.pk}/{filename}'


class NoteFile(models.Model):
    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_to_note_file, max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name if self.file else 'Archivo sin nombre'

    class Meta:
        verbose_name = 'Archivo de nota'
        verbose_name_plural = 'Archivos de nota'
