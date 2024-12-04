from rest_framework import views, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from api.note.serializers import (
    NoteLinkAndContentSerializer, NoteLinkSerializer,
    BasicNoteContentSerializer, NoteLinkFullSerializer)
from news.models import ApplyQuery, NoteLink, NoteContent, Source, SourceMethod
from utils.open_ai import JsonRequestOpenAI


class NoteContentViewSet(ModelViewSet):
    queryset = NoteContent.objects.all()
    serializer_class = NoteLinkAndContentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"])
    def additional_info(self, request, pk=None):
        note_content = self.get_object()
        note_open_ai = JsonRequestOpenAI('news/note_prompt.txt')
        try:
            json_content = note_open_ai.send_prompt(note_content.content)
        except Exception:
            raise ValidationError("No se pudo extraer el contenido por OpenAI")
        note_content.structured_content = json_content
        note_content.save()
        return Response(json_content)

    def list(self, request):
        # Todo LUCIAN: Filtrar según NoteLink.source
        # y por rango de fechas (gte y lte) según NoteLink.published_at
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NoteLinkViewSet(ModelViewSet):
    queryset = NoteLink.objects.all()
    serializer_class = NoteLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        actions = {
            "list": NoteLinkSerializer,
            "create": NoteLinkFullSerializer,
            "manual_create_note_content": NoteLinkFullSerializer,
        }
        return actions.get(self.action, self.serializer_class)

    @action(detail=True, methods=["patch"])
    def get_note_content(self, request, pk=None):
        from news.note_utils import GetNoteContent

        serializer = NoteLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_link = serializer.save()

        note_content = GetNoteContent(new_link)
        return note_content()

    @action(detail=True, methods=["patch"])
    def manual_create_note_content(self, request, pk=None):
        request.data['note_link'] = pk
        serializer = BasicNoteContentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        note_link = self.get_object()
        new_content = NoteLinkFullSerializer(note_link).data

        return Response(new_content)

    def list(self, request):
        # Todo LUCIAN: Recibir filtro de has_notes (Booleano)
        # También un filtro is_dfi (Booleano)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
