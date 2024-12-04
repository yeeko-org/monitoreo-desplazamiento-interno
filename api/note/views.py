from rest_framework import views, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from api.note.serializers import NoteAndLinkSerializer, LinkFullSerializer
from news.models import ApplyQuery, Link, Note, Source, SourceMethod
from utils.open_ai import JsonRequestOpenAI


class NoteContentView(views.APIView):

    def post(self, request, *args, **kwargs):
        from news.note_utils import NoteContent

        data: dict = request.data

        gnews_source = data.get("gnews_source")
        source, source_created = Source.objects.get_or_create(
            main_url=gnews_source.get("href"),
            defaults={"name": gnews_source.get("title")},
        )

        link_valid = data.get("is_dfi")
        if not isinstance(link_valid, bool):
            link_valid = None

        title = data.get("title")
        real_url = data.get("real_url")
        link, link_is_created = Link.objects.get_or_create(
            gnews_url=data.get("gnews_url"),
            defaults=dict(
                real_url=real_url,
                title=title,
                source=source,
                published_at=data.get("published_at"),
                is_dfi=link_valid,
            )
        )

        apply_query_id = data.get("apply_query_id")
        if apply_query_id:
            try:
                query_origin = ApplyQuery.objects.get(pk=apply_query_id)
                link.queries.add(query_origin)
            except ApplyQuery.DoesNotExist:
                pass

        if not link_is_created:
            link.is_dfi = link_valid
            if real_url:
                link.real_url = real_url
            link.save()

        note_content = NoteContent(link, source)
        return note_content()


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteAndLinkSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"])
    def aditional_info(self, request, pk=None):
        note = self.get_object()
        note_open_ai = JsonRequestOpenAI('news/note_prompt.txt')
        try:
            json_content = note_open_ai.send_prompt(note.content)
        except Exception:
            raise ValidationError("No se pudo extraer el contenido por OpenAI")
        note.structured_content = json_content
        note.save()
        return Response(json_content)


class LinkViewSet(ModelViewSet):
    queryset = Link.objects.all()
    # serializer_class = NoteAndLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        actions = {
            "get_note_content": LinkFullSerializer,
        }

    @action(detail=True, methods=["post"])
    def get_note_content(self, request, pk=None):
        from news.note_utils import NoteContent
        link = self.get_object()

        serializer = self.get_serializer(data=request.data)

        note_content = NoteContent(link)
        return note_content()
