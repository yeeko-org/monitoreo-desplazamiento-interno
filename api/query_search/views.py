from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
# from urllib.parse import unquote
from abc import ABC, abstractmethod
from news.models import ApplyQuery, NoteLink, SearchQuery, NoteContent, Source
from api.query_search.serializers import (
    ApplyQuerySerializer, SearchQuerySerializer, WhenSerializer)
from api.note.serializers import (
    NoteLinkFullSerializer, NoteLinkSerializer)
from api.catalogs.serializers import SourceSerializer
from typing import Optional


class SearchMixin:

    apply_query: Optional[ApplyQuery] = None
    built_note_links: list = []

    @abstractmethod
    def get_search_query(self) -> SearchQuery:
        raise NotImplementedError

    @abstractmethod
    def get_when_data(self):
        raise NotImplementedError

    def get_link_serializer(self, link_instance):
        if self.apply_query:
            link_instance.queries.add(self.apply_query)
        note_link_data = NoteLinkFullSerializer(link_instance).data
        self.built_note_links.append(note_link_data)

    def search_data(self):
        from utils.date_time import parse_gmt_date_list
        search_query = self.get_search_query()
        when_data = self.get_when_data()

        links_data = search_query.search(**when_data)
        search_entries = links_data['entries']
        feed = links_data.get('feed')
        errors = links_data.get('errors', [])

        if self.apply_query:
            save_apply_query = False
            if feed:
                self.apply_query.last_feed = feed
                save_apply_query = True

            if errors:
                self.apply_query.add_errors(errors, save=False)
                save_apply_query = True

            if save_apply_query:
                self.apply_query.save()

        print("search_entries ready")
        self.built_note_links = []

        for entry in search_entries:

            gnews_url = entry.pop('link')
            note_link_obj = NoteLink.objects.filter(
                gnews_url=gnews_url).first()
            if note_link_obj:
                self.get_link_serializer(note_link_obj)
                continue

            title = entry.pop('title')
            source = entry.pop('source')
            entry['gnews_source'] = source
            pre_link = {
                "gnews_entry": entry,
                "gnews_url": gnews_url,
            }
            split = title.rsplit(' - ', 1)
            if len(split) == 2:
                pre_link['title'] = split[0]
            else:
                pre_link['title'] = title
            published_parsed = entry.pop('published_parsed')
            published_at = parse_gmt_date_list(published_parsed)
            if published_at:
                published_at = published_at.strftime('%Y-%m-%d %H:%M:%S')
            else:
                published_at = None

            pre_link["published_at"] = published_at

            if self.apply_query:
                pre_national = source.get('pre_national')
                if pre_national not in ["Nal", "Int", "For"]:
                    pre_national = None
                source_obj, source_obj_created = Source.objects.get_or_create(
                    main_url=source['href'],
                    defaults={
                        "name": source['title'],
                        "pre_national": pre_national,
                    }
                )
                pre_link['source'] = source_obj.pk
                note_link_serializer = NoteLinkSerializer(data=pre_link)
                note_link_serializer.is_valid(raise_exception=True)
                note_link_obj = note_link_serializer.save()
                self.get_link_serializer(note_link_obj)

            else:
                source_obj = Source.objects.filter(
                    main_url=source['href']).first()
                if source_obj:
                    source_serializer = SourceSerializer(source_obj)
                    pre_link['source'] = source_serializer.data
                else:
                    pre_link['source'] = {
                        "name": source['title'],
                        "main_url": source['href'],
                    }
                self.built_note_links.append(pre_link)

        return {
            'search_count': len(self.built_note_links),
            'note_links': self.built_note_links,
            'feed': links_data.get('feed'),
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
        when_serializer = self.get_serializer(
            data=self.request.data)  # type: ignore

        when_serializer.is_valid(raise_exception=True)
        return when_serializer.validated_data

    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        self.apply_query = None
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
            'when': None,
            'from_date': apply_query.from_date,
            'to_date': apply_query.to_date,
        }

    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        self.apply_query = self.get_object()
        try:
            search_query_data = self.search_data()
        except Exception as e:
            self.apply_query.add_errors(str(e))
            raise ValidationError(str(e))
            # raise e  # para debug
        for entry in search_query_data['note_links']:
            entry['apply_query'] = pk
        return Response(search_query_data)
