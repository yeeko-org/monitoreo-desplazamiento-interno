from django.db import models

from pygooglenews import GoogleNews
import requests
from category.models import StatusControl


class Source(models.Model):
    name = models.CharField(max_length=100)
    is_news = models.BooleanField(
        default=True, verbose_name='Es una fuente de noticias')
    main_url = models.CharField(max_length=100, blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'


class SearchQuery(models.Model):
    query = models.TextField()
    when = models.CharField(max_length=10, default='1d')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query

    def save(self, *args, **kwargs):

        _save = super().save(*args, **kwargs)
        gn = GoogleNews("es", "MX")
        notes = gn.search(self.query, helper=True, when=self.when)
        entries = notes['entries']
        for entry in entries:
            source = entry.get("source", {}).get("href")

            link = Link.objects.create(
                query=self,
                gnews_url=entry.get("link"),
                title=entry.get("title"),
                description=entry.get("summary"),
                source=source
            )
            link.save()
        return _save


class Link(models.Model):
    query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='links')
    gnews_url = models.URLField(max_length=800)
    real_url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    source = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.gnews_url[:30]

    def get_content(self):
        response = requests.get(self.gnews_url)
        if response.status_code == 200:
            if not self.real_url:
                self.real_url = response.url
                self.save()
            return response.content
        return None


class SourceMethod(models.Model):
    domain = models.CharField(max_length=200)
    title_tag = models.CharField(max_length=200)
    subtitle_tag = models.CharField(max_length=200)
    content_tag = models.TextField()

    def __str__(self):
        return self.domain

    def notes_by_link(self, link: Link):
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

        notes = Note.objects.create(
            link=link,
            title=title,
            subtitle=subtitle,
            content=content,
            source_method=self
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
    subtitle = models.CharField(max_length=200)
    content = models.TextField()
    structured_content = models.JSONField(blank=True, null=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

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
