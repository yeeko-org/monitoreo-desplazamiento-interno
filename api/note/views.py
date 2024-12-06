from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django_filters import FilterSet, DateFilter, CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from api.common_views import BaseViewSet
from api.note.serializers import (
    NoteLinkAndContentSerializer, NoteLinkSerializer,
    BasicNoteContentSerializer, NoteLinkFullSerializer,
    NoteLinkSpecialSerializer)
from news.models import ApplyQuery, NoteLink, NoteContent, Source, SourceMethod
from utils.open_ai import JsonRequestOpenAI
from api.pagination import CustomPagination


class NoteContentFilter(FilterSet):

    # start_date = DateFilter(field_name='date', lookup_expr='gte')
    # end_date = DateFilter(field_name='date', lookup_expr='lte')
    status_register = CharFilter(field_name='status_register__name')

    class Meta:
        model = NoteContent
        fields = {'source': ['exact']}


class NoteContentViewSet(ModelViewSet):
    queryset = NoteContent.objects.all()
    serializer_class = NoteLinkAndContentSerializer
    permission_classes = [IsAuthenticated]

    filterset_class = NoteContentFilter
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "title",
    ]

    @action(detail=True, methods=["get"])
    def additional_info(self, request, pk=None):
        note_content = self.get_object()
        note_open_ai = JsonRequestOpenAI(
            'news/structure_prompt.txt', to_json=False)
        try:
            subtitle = note_content.subtitle
            date = note_content.note_link.published_at
            full_content = (f"{note_content.title}\n{subtitle} ({date})"
                            f"\n\n{note_content.content}")
            text_content = note_open_ai.send_prompt(full_content)
        except Exception as e:
            print("Error en la extracción de contenido", e)
            raise ValidationError("No se pudo extraer el contenido por OpenAI")
        note_content.structured_content = text_content
        note_content.save()
        return Response({"structured_content": text_content})


class NoteLinkFilter(FilterSet):

    start_date = DateFilter(field_name='date', lookup_expr='gte')
    end_date = DateFilter(field_name='date', lookup_expr='lte')
    status_register = CharFilter(field_name='status_register__name')
    source_origin = NumberFilter(
        field_name='source__source_origin', lookup_expr='exact')

    class Meta:
        model = NoteLink
        fields = {'source': ['exact']}


class NoteLinkViewSet(ModelViewSet):
    queryset = NoteLink.objects.all()
    serializer_class = NoteLinkSerializer
    permission_classes = [IsAuthenticated]

    filterset_class = NoteLinkFilter
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    pagination_class = CustomPagination
    search_fields = ["title"]

    def get_serializer_class(self):
        actions = {
            "list": NoteLinkSerializer,
            "retrieve": NoteLinkFullSerializer,
            "manual_create_note_content": NoteLinkFullSerializer,
        }
        return actions.get(self.action, self.serializer_class)

    @action(detail=True, methods=["patch"])
    def get_note_content(self, request, pk=None):
        from news.note_utils import GetNoteContent

        note_link = self.get_object()
        serializer = NoteLinkSpecialSerializer(
            note_link, data=request.data, partial=True)
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
