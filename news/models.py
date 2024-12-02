from datetime import date, datetime
from typing import Optional, Any
from bs4 import BeautifulSoup
import requests

from django.db import models
from utils.yeeko_gnews import YeekoGoogleNews

from category.models import StatusControl
from utils.date_time import parse_gmt_date_list


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
    main_word = models.CharField(max_length=100, unique=True)
    alternative_words = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

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
            self, when: Any, from_date: Optional[date],
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
            try:
                when = int(when)
                when = f"{when}d"
            except ValueError:
                pass
            search_kwargs = {"when": when or "1d"}
        # gn = GoogleNews("es", "MX")
        gn = YeekoGoogleNews("es", "MX")
        print("Searching...\n", final_query, "\n", search_kwargs)
        notes_data = gn.search(final_query, helper=False, **search_kwargs)
        # for key, value in notes_data.items():
        #     if key != "entries":
        #         print(key, value)
        return notes_data

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class ApplyQuery(models.Model):

    search_query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='applied')
    created_at = models.DateTimeField(auto_now_add=True)
    when = models.CharField(
        max_length=10, help_text='1d', blank=True, null=True
    )
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    def search_and_save_entries(self):
        notes_data = self.search_query.search(
            self.when, self.from_date, self.to_date)
        entries = notes_data.get("entries")

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
        link.queries.add(self)
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
    # description = models.TextField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='links')
    published_at = models.DateTimeField(blank=True, null=True)
    queries = models.ManyToManyField(
        ApplyQuery, related_name='links', blank=True)
    # valid = models.BooleanField(blank=True, null=True)
    is_dfi = models.BooleanField(blank=True, null=True)

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

    def get_content_text_rick(self):
        # response = self.get_response()
        # if not response:
        #     return ""
        # response = requests.get(
        #     'https://www.infobae.com/mexico/2024/11/30/desplazamiento-forzado-en-sinaloa-una-violencia-que-ataca-por-tres-frentes/')
        # response = requests.get(
        #     'https://www.milenio.com/politica/comunidad/cierra-plaza-izazaga-89-tras-operativo-contra-contrabando-en-cdmx')
        # response = requests.get(
        #     'https://laverdadnoticias.com/crimen/crisis-en-sinaloa-18-mil-familias-desplazadas-por-violencia-y-sequias-20241130')
        # title = "Crisis en Sinaloa: 18 mil familias desplazadas por violencia y sequías"
        response = requests.get(
            'https://programasparaelbienestar.gob.mx/con-programas-para-el-bienestar-gobierno-atiende-a-pobladores-desplazados-en-chiapas/')
        title = "Con Programas para el Bienestar, Gobierno atiende a pobladores desplazados en Chiapas"
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        body = soup.body
        if title not in body.get_text():
            title = None

        excluded_tags = [
            'script', 'style', 'noscript', 'svg', 'button', 'input',
            'textarea', 'select', 'option', 'form', 'fieldset', 'canvas',
            'nav', 'aside', 'address', 'map', 'area',
            'legend', 'iframe', 'embed', 'object', 'param', 'video', 'audio']
        for excluded_tag in excluded_tags:
            for tag in body.find_all(excluded_tag):
                tag.decompose()
        main_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']
        begin_title = not bool(title)
        for tag in body.find_all():
            tag_text = tag.get_text(strip=True)
            if not tag_text and tag.name not in main_tags:
                tag.decompose()
            if not begin_title:
                direct_text = tag.string
                if direct_text and title in direct_text:
                    begin_title = True
            if not begin_title:
                if title not in tag_text:
                    tag.decompose()

        allowed_attrs = ['class', 'id', 'href', 'src', 'alt', 'title']
        # new_body = BeautifulSoup('', 'html.parser')
        for tag in body.find_all():
            relevant_attrs = {
                key: value for key, value in tag.attrs.items()
                if key in allowed_attrs
            }
            tag.attrs = relevant_attrs
        # print("Body3:", body.prettify())
        new_html = body.prettify()
        return new_html, body.get_text(separator="\n")


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

    def note_by_link_rick(self, link: Link, saved_title: str = None):
        from bs4 import BeautifulSoup
        link_content = link.get_content()
        if not link_content:
            return None
        soup = BeautifulSoup(link_content, 'html.parser')

        def get_element(tag_info: dict):
            elem_id = tag_info.get("id")
            elem_class = tag_info.get("class")
            elem_tag = tag_info.get("tag")
            if elem_tag:
                return soup.find(elem_tag, id=elem_id, class_=elem_class)
            else:
                return soup.find(id=elem_id, class_=elem_class)

        def get_data(key):
            if value := self.tags.get(key):
                element = get_element(value)
                if not element:
                    return None
                return element.get_text(separator="\n", strip=True)

        title = saved_title or get_data('title')
        content = get_data('content')
        if not (title and content):
            return None

        return Note.objects.create(
            title=title,
            content=content,
            link=link,
            source_method=self,
            source=link.source,
            subtitle=get_data('subtitle'),
            author=get_data('author'),
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Método de fuente'
        verbose_name_plural = 'Métodos de fuente'


class Note(models.Model):
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE,
        verbose_name='Fuente de información')
    link = models.ForeignKey(
        Link, on_delete=models.CASCADE, related_name='notes')
    source_method = models.ForeignKey(
        SourceMethod, on_delete=models.CASCADE, related_name='notes',
        null=True, blank=True)

    title = models.CharField(max_length=255)
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
