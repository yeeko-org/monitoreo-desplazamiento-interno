from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.note.serializers import NoteAndLinkSerializer
from news.models import Link, Note, Source, SourceMethod
from news.open_ai_note import NoteOpenAI
from utils.date_time import parse_gmt_date_list
from utils.open_ai import truncate_text


class NoteContentView(views.APIView):
    def post(self, request, *args, **kwargs):
        data: dict = request.data

        source_name = data.get("source", {}).get("title")
        source_url = data.get("source", {}).get("href")
        source, _ = Source.objects.get_or_create(
            name=source_name,
            defaults={"main_url": source_url}
        )

        link_valid = data.get("link_valid")
        if not isinstance(link_valid, bool):
            link_valid = None

        link, link_is_created = Link.objects.get_or_create(
            gnews_url=data.get("link"),
            defaults=dict(
                real_url=data.get("real_url"),
                title=data.get("title"),
                description=data.get("summary"),
                source=source,
                published_at=parse_gmt_date_list(
                    data.get("published_parsed")),
                valid=link_valid
            )
        )

        if not link_is_created:
            link.valid = link_valid
            link.real_url = data.get("real_url")
            link.save()

        data["link_valid"] = link.valid
        data["link_id"] = link.pk

        if link_valid is False:
            return Response(data)

        if not link.real_url:
            data["errors"] = [
                "Se requiere una URL real para obtener el contenido"]
            return Response(data)

        notes = Note.objects.filter(link=link).select_related("link")
        notes_data = NoteAndLinkSerializer(notes, many=True).data

        if notes_data:
            data["notes"] = notes_data
            return Response(data)

        source_method = SourceMethod.objects.filter(
            sources__id=source.pk).first()

        if source_method:
            note = source_method.note_by_link(link)
            if note:
                data["notes"] = [NoteAndLinkSerializer(note).data]
                return Response(data)

        link_content_text = link.get_content_text()
        if not link_content_text:
            return Response(data)
        truncate_data = truncate_text(link_content_text)

        link_content_text = truncate_data.get("truncated_text")

        note_open_ai = NoteOpenAI()
        json_content = note_open_ai.extract_information(link_content_text)
        if not json_content:
            return Response(data)
        
        if not all([key in json_content for key in ["title", "content"]]):
            data["errors"] = ["No se pudo extraer el contenido por OpenAI"]
            return Response(data)

        note = Note.objects.create(
            link=link,
            source=source,
            title=json_content.get("title"),
            subtitle=json_content.get("subtitle"),
            content=json_content.get("content"),
        )

        data["notes"] = [NoteAndLinkSerializer(note).data]
        return Response(data)


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteAndLinkSerializer
    permission_classes = [IsAuthenticated]
