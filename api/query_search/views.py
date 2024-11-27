from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from news.models import Link, SearchQuery, Note
from api.query_search.serializers import SearchQuerySerializer
from api.note.serializers import NoteAndLinkSerializer


class SearchQueryViewSet(ModelViewSet):
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        search_query = self.get_object()
        search_entries = search_query.search()
        exist_links_count = 0
        for entries in search_entries:
            link_url = entries.get('link')
            link_obj = Link.objects.filter(gnews_url=link_url).first()
            if not link_obj:
                continue

            notes = Note.objects.filter(link=link_obj)
            note_serializer = NoteAndLinkSerializer(notes, many=True)
            entries['notes'] = note_serializer.data
            entries["link_id"] = link_obj.pk
            entries["link_valid"] = link_obj.valid
            exist_links_count += 1
        search_count = len(search_entries)
        return Response({
            'search_count': search_count,
            'exist_links_count': exist_links_count,
            'search_entitys': search_entries,
        })
