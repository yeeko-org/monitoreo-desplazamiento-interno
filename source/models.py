from typing import TYPE_CHECKING
from bs4 import BeautifulSoup

from django.db import models

if TYPE_CHECKING:
    from note.models import NoteLink


class SourceOrigin(models.Model):

    name = models.CharField(max_length=100)
    old_name = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    order = models.SmallIntegerField(default=5)
    in_scope = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Origen de fuente (National)'
        verbose_name_plural = 'Orígenes de fuente (National)'


class Source(models.Model):

    NATIONAL_CHOICES = [
        ('Nal', 'Nacional'),
        ('Int', 'Internacional'),
        ('For', 'Extranjera'),
    ]

    name = models.CharField(max_length=100)
    main_url = models.CharField(max_length=100, blank=True, null=True)
    source_origin = models.ForeignKey(
        SourceOrigin, on_delete=models.CASCADE,
        related_name='sources', default=1)  # type: ignore
    origin_checked = models.BooleanField(
        default=False, verbose_name='Origen verificado')
    has_content = models.BooleanField(
        blank=True, null=True, verbose_name='Es scrapeable')
    scraper_message = models.TextField(blank=True, null=True)
    # national = models.CharField(
    #     choices=NATIONAL_CHOICES, max_length=3, blank=True, null=True)
    is_active = models.BooleanField(
        blank=True, null=True, verbose_name='Activa')

    # pre_national = models.CharField(
    #     choices=NATIONAL_CHOICES, max_length=3, blank=True, null=True)
    pre_source_origin = models.ForeignKey(
        SourceOrigin, on_delete=models.CASCADE, blank=True, null=True,
        related_name='pre_sources')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'


class SourceMethod(models.Model):

    name = models.CharField(max_length=200)

    title_tag = models.CharField(
        max_length=200, blank=True, null=True)
    subtitle_tag = models.CharField(
        max_length=200, blank=True, null=True)
    content_tag = models.TextField(blank=True, null=True)
    tags = models.JSONField(blank=True, null=True)

    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='methods')

    def content_by_link(self, note_link: "NoteLink"):
        from note.models import NoteContent
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
