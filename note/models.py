
from bs4 import BeautifulSoup
import requests

from django.db import models

from category.models import StatusControl
from source.models import Source, SourceMethod
from search.models import ApplyQuery

REQUESTS_DEFAULT_HEADERS = {'User-Agent': 'Mozilla/4.0'}


class NoteLink(models.Model):

    INTERNAL_DIS_CHOICES = [
        ('valid', 'Válido'),
        ('invalid', 'Inválido'),
        ('unknown', 'Desconocido'),
    ]

    gnews_url = models.URLField(max_length=1500, unique=True)
    real_url = models.URLField(max_length=800, blank=True, null=True)
    title = models.TextField()
    # description = models.TextField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='note_links')
    published_at = models.DateTimeField(blank=True, null=True)
    queries = models.ManyToManyField(
        ApplyQuery, related_name='note_links', blank=True)
    gnews_entry = models.JSONField(blank=True, null=True)
    is_dfi = models.BooleanField(blank=True, null=True)
    is_internal_dis = models.CharField(
        choices=INTERNAL_DIS_CHOICES, max_length=10, blank=True, null=True)
    pre_is_dfi = models.BooleanField(blank=True, null=True)

    note_contents: models.QuerySet["NoteContent"]

    def __str__(self):
        return self.gnews_url[:30]

    def get_response(self):
        response = requests.get(
            self.real_url or self.gnews_url, headers=REQUESTS_DEFAULT_HEADERS)
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

    # structured_content = models.JSONField(blank=True, null=True)
    structured_content = models.TextField(blank=True, null=True)

    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # link_content_text = models.TextField(blank=True, null=True)

    files: models.QuerySet["NoteFile"]
    status_register_id = str | None

    def __str__(self):
        return self.title or self.note_link.title

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
