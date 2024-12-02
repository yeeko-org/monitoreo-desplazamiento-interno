from news.models import Link, Note, SourceMethod, Source
from api.catalogs.serializers import SourceSerializer
from utils.open_ai import JsonRequestOpenAI
from rest_framework.response import Response
from api.note.serializers import NoteAndLinkSerializer


class HttpResponseError(Exception):

    def __init__(self, body_response=None, http_status=400):
        self.body_response = body_response or {}
        self.http_status = http_status
        self.errors = body_response.get("errors", [])
        super().__init__(self.body_response)

    def send_response(self):
        from rest_framework.response import Response
        return Response(self.body_response, status=self.http_status)


class NoteContent:

    def __init__(self, link: Link, source: Source = None):
        self.first_response = None
        self.first_example = None
        self.prompt = None
        self.link = link
        self.real_url = link.real_url
        if not source:
            source = link.source
        self.source = source
        self.full_html = None
        self.full_text = None

        self.response_data = {
            "link": {
                "is_dfi": link.is_dfi, "id": link.pk
            },
            "source": SourceSerializer(source).data
        }

    def __call__(self):
        import traceback
        try:
            return self.get_notes()
        except HttpResponseError as e:
            e.body_response.update(self.response_data)
            return e.send_response()
        except Exception as e:
            error = f"Hubo un error: {e}"
            print(traceback.format_exc())
            return Response({"errors": [error]}, status=500)

    def get_notes(self):

        if self.link.is_dfi is False:
            raise HttpResponseError(self.response_data, http_status=200)

        if not self.link.real_url:
            error = "Se requiere una URL real para obtener el contenido"
            raise HttpResponseError({"errors": [error]})

        saved_notes = Note.objects.filter(link=self.link).select_related("link")
        if saved_notes.exists():
            self.send_notes(saved_notes)

        source_methods = SourceMethod.objects.filter(
            source=self.source, tags__isnull=False)
        for source_method in source_methods:
            self.get_note_by_method(source_method)
        self.build_tags()

    def build_tags(self):
        self.get_reduced_content_text(self.real_url)
        if not self.full_text:
            error = "No se pudo obtener el contenido vía BeautifulSoup"
            raise HttpResponseError({"errors": [error]})

        full_prompt = f"The title previously mentioned is: {self.link.title}\n"
        full_prompt += self.full_html\
            .encode("utf-8", errors="ignore")\
            .decode("utf-8")

        tags_open_ai = JsonRequestOpenAI("news/prompt_tags.txt")
        tags_content = tags_open_ai.send_prompt(full_prompt)
        print("tags_content", tags_content)
        if not tags_content:
            error = "No se pudo obtener el contenido de las etiquetas"
            raise HttpResponseError({"errors": [error]})
        has_content = tags_content.get("has_content", None)
        if isinstance(has_content, bool):
            self.source.has_content = has_content
            self.source.is_active = has_content
            self.source.save()
        gpt_message = tags_content.get("message", None)
        if gpt_message and not self.source.scraper_message:
            self.source.scraper_message = gpt_message
            self.source.save()
        self.response_data["source"] = SourceSerializer(self.source).data
        source_method = SourceMethod.objects.create(
            name=f"Tags {self.source.name}",
            source=self.source,
            tags=tags_content)
        if has_content is False:
            errors = [gpt_message, "No se encontró contenido en la URL"]
            raise HttpResponseError({"errors": errors})
        # self.link.source_method = source_method
        self.get_note_by_method(
            source_method, forced_error=True)

        error = "Error desconocido"
        raise HttpResponseError({"errors": [error]})

    def send_notes(self, notes: list[Note]):
        note_serializer = NoteAndLinkSerializer(notes, many=True)
        self.response_data["notes"] = note_serializer.data
        raise HttpResponseError(self.response_data, http_status=200)

    def get_note_by_method(self, source_method: SourceMethod, forced_error=False):
        from bs4 import BeautifulSoup

        if self.full_html:
            soup = BeautifulSoup(self.full_html, 'html.parser')
        else:
            link_content = self.link.get_content()
            if not link_content:
                if forced_error:
                    error = "No se pudo obtener el contenido de la URL"
                    raise HttpResponseError({"errors": [error]})
                return None
            soup = BeautifulSoup(link_content, 'html.parser')

        def get_elements(tag_info: dict):
            elem_tag = tag_info.get("tag")
            kwargs = {}
            if elem_id := tag_info.get("id"):
                kwargs["id"] = elem_id
            if elem_class := tag_info.get("class"):
                kwargs["class_"] = elem_class
            if elem_tag:
                return soup.find_all(elem_tag, **kwargs)
            elif kwargs:
                return soup.find_all(**kwargs)
            return []

        def get_element_content(key):
            if value := source_method.tags.get(key):
                elements = get_elements(value)
                if not elements:
                    return None, None
                pretty_final = ""
                final_text = ""
                for element in elements:
                    pretty_final += element.prettify()\
                        .encode("utf-8", errors="ignore").decode("utf-8")
                    final_text += element.get_text(separator="\n", strip=True)
                    if value.get("multiple") is False:
                        break
                return pretty_final, final_text
            return None, None

        title = self.link.title
        if not title:
            _, title = get_element_content('title')
        content_full, content = get_element_content('content')
        if not (title and content):
            if forced_error:
                error = "No se encontraron las etiquetas necesarias"
                # print("soup final:", soup.prettify().encode("utf-8", errors="ignore"))
                raise HttpResponseError({"errors": [error]})
            return None

        _, subtitle = get_element_content('subtitle')
        _, author = get_element_content('author')

        final_note = Note.objects.create(
            title=title,
            content=content,
            content_full=content_full,
            link=self.link,
            source_method=source_method,
            source=self.source,
            subtitle=subtitle,
            author=author,
            full_html=self.full_html,
            full_text=self.full_text,
        )

        self.send_notes([final_note])

    def get_reduced_content_text(self, url: str):
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(url)
        # response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, "html.parser")
        body = soup.body
        body = body
        title = self.link.title
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
        main_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'ul']
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
        try:
            # body_encoding = body.encode("utf-8")
            self.full_html = body.prettify()\
                .encode("utf-8", errors="ignore").decode("utf-8")
            # print("Body4:", self.full_html)
        except Exception as e:
            print("Error body.pretty:", e)
            print("-" * 50)
            print("Body5:", body)
            raise e
        # new_html = body.prettify()
        self.full_text = body.get_text(separator="\n")
        # return new_html, body.get_text(separator="\n")
