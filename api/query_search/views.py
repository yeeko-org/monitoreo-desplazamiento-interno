from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
# from urllib.parse import unquote
from abc import ABC, abstractmethod
from news.models import ApplyQuery, Link, SearchQuery, Note, Source
from api.query_search.serializers import (
    ApplyQuerySerializer, SearchQuerySerializer, WhenSerializer)
from api.note.serializers import NoteAndLinkSerializer, LinkSimpleSerializer
from api.catalogs.serializers import SourceSerializer


class SearchMixin:
    @abstractmethod
    def get_search_query(self) -> SearchQuery:
        raise NotImplementedError

    @abstractmethod
    def get_when_data(self):
        raise NotImplementedError

    def search_data(self):
        from utils.date_time import parse_gmt_date_list
        search_query = self.get_search_query()
        when_data = self.get_when_data()

        notes_data = search_query.search(**when_data)
        search_entries = notes_data['entries']
        print("search_entries ready")
        exist_links_count = 0
        for entry in search_entries:
            gnews_url = entry.pop('link')
            entry['gnews_url'] = gnews_url
            entry['gnews_id'] = entry.pop('id')
            source = entry.pop('source')
            entry['gnews_source'] = source
            title = entry.pop('title')
            split = title.rsplit(' - ', 1)
            if len(split) == 2:
                entry['title'] = split[0]
            else:
                entry['title'] = title
            published_parsed = entry.pop('published_parsed')
            # entry["published_at"] = parse_gmt_date_list(published_parsed)
            published_at = parse_gmt_date_list(published_parsed)
            published_at = published_at.strftime('%Y-%m-%d %H:%M:%S')
            entry["published_at"] = published_at

            source_obj = Source.objects.filter(
                main_url=source['href']).first()
            if source_obj:
                source_serializer = SourceSerializer(source_obj)
                entry['source'] = source_serializer.data
            else:
                entry['source'] = {}

            link_obj = Link.objects.filter(gnews_url=gnews_url).first()
            if not link_obj:
                continue

            notes = Note.objects.filter(link=link_obj)
            note_serializer = NoteAndLinkSerializer(notes, many=True)
            entry['notes'] = note_serializer.data
            # entry["link_id"] = link_obj.pk
            # entry["link_valid"] = link_obj.valid
            entry["link_full"] = LinkSimpleSerializer(link_obj).data
            exist_links_count += 1
        search_count = len(search_entries)
        return {
            'search_count': search_count,
            'exist_links_count': exist_links_count,
            'search_entries': search_entries,
            'feed': notes_data.get('feed'),
        }


class SearchQueryViewSet(SearchMixin, ModelViewSet):
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):  # type: ignore
        actions = {
            "search": WhenSerializer,
        }
        try:
            return actions.get(self.action, self.serializer_class)
        except Exception:
            pass

        return super().get_serializer_class()

    def get_search_query(self) -> SearchQuery:
        return self.get_object()

    def get_when_data(self):
        when_serializer = self.get_serializer(data=self.request.data)

        when_serializer.is_valid(raise_exception=True)
        return when_serializer.validated_data

    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        return Response(self.search_data())


class ApplyQueryViewSet(SearchMixin, ModelViewSet):
    queryset = ApplyQuery.objects.all()
    serializer_class = ApplyQuerySerializer
    permission_classes = [IsAuthenticated]

    def get_search_query(self) -> SearchQuery:
        return self.get_object().search_query

    def get_when_data(self):
        apply_query: ApplyQuery = self.get_object()
        return {
            'when': apply_query.when,
            'from_date': apply_query.from_date,
            'to_date': apply_query.to_date,
        }

    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        search_query_data = self.search_data()
        for entry in search_query_data['search_entries']:
            entry['apply_query'] = pk
        return Response(search_query_data)
