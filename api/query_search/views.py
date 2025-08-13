from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
# from urllib.parse import unquote
from abc import ABC, abstractmethod
from source.models import Source
from search.models import ApplyQuery, SearchQuery
from note.models import NoteLink
from api.query_search.serializers import (
    ApplyQuerySerializer, SearchQuerySerializer, WhenSerializer,
    ApplyQueryFullSerializer, SearchQueryFullSerializer)
from api.note.serializers import (
    NoteLinkFullSerializer, NoteLinkSerializer)
from api.catalogs.serializers import SourceSerializer, PreSourceSerializer
from search.gnews_search import GNewsSearch
from typing import List, Optional, Any, Union
from datetime import date


class SearchMixin:

    apply_query: Optional[ApplyQuery] = None
    built_note_links: list = []
    search_service: GNewsSearch = None

    @abstractmethod
    def add_link_full_data(self, note_link: NoteLink):
        raise NotImplementedError(
            "add_link_full_data method must be implemented in the subclass")

    @abstractmethod
    def save_note_link(self, source_data: dict, pre_link: dict):
        raise NotImplementedError(
            "save_note_link method must be implemented in the subclass")

    def search_note_data(
            self, search_query: SearchQuery,
            when: Optional[Any] = None, from_date: Optional[date] = None,
            to_date: Optional[date] = None
    ):

        final_query, all_negative_words = search_query.get_final_query()

        self.search_service = GNewsSearch(
            final_query, when, from_date, to_date, all_negative_words)
        self.search_service.search_in_gnews()

        self.built_note_links = []

        for entry in self.search_service.search_entries:

            gnews_url = entry.pop('link')
            note_link_obj = NoteLink.objects\
                .filter(gnews_url=gnews_url)\
                .first()
            if note_link_obj:
                self.add_link_full_data(note_link_obj)
                continue

            title = entry.pop('title')
            source = entry.pop('source')
            entry['gnews_source'] = source
            # pre_valid_option = entry.pop('pre_valid_option', None)
            pre_link = {
                "gnews_entry": entry,
                "gnews_url": gnews_url,
                "note_contents": [],
                "published_at": self._date_to_str(entry),
                # "pre_valid_option": pre_valid_option,
            }
            split = title.rsplit(' - ', 1)
            if len(split) == 2:
                pre_link['title'] = split[0]
            else:
                pre_link['title'] = title

            self.save_note_link(source, pre_link)

        return {
            'search_count': len(self.built_note_links),
            'note_links': self.built_note_links,
            'feed': self.search_service.feed,
        }

    def _date_to_str(self, entry: dict):
        from utils.date_time import parse_gmt_date_list
        published_parsed = entry.get('published_parsed')
        published_at = parse_gmt_date_list(published_parsed)
        if published_at:
            return published_at.strftime('%Y-%m-%d %H:%M:%S')
        return None


class SearchQueryViewSet(SearchMixin, ModelViewSet):
    queryset = SearchQuery.objects.all()
    # serializer_class = SearchQuerySerializer
    serializer_class = SearchQueryFullSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):  # type: ignore
        actions = {
            "search": WhenSerializer,
            "list": SearchQuerySerializer,
        }
        try:
            return actions.get(self.action, self.serializer_class)
        except Exception:
            pass

        return super().get_serializer_class()

    def add_link_full_data(self, note_link: NoteLink):
        note_link_data = NoteLinkFullSerializer(note_link).data
        self.built_note_links.append(note_link_data)

    def save_note_link(self, source_data: dict, pre_link: dict):
        href = source_data.get('href')
        title = source_data.get('title')
        source_obj = Source.objects.filter(main_url=href, name=title).first()
        if source_obj:
            source_serializer = PreSourceSerializer(source_obj)
            pre_link['source_full'] = source_serializer.data
        else:
            pre_link['source_full'] = {"name": title, "main_url": href}
        self.built_note_links.append(pre_link)

    @action(detail=True, methods=['post'])
    def search(self, request, pk=None):
        self.apply_query = None
        search_query = self.get_object()

        when_str = request.data.get('when', "")
        if not when_str:
            return Response(
                {"errors": ["Se requiere el campo 'when'"]},
                status=400
            )
        search_query_data = self.search_note_data(search_query, when=when_str)
        return Response(search_query_data)


class ApplyQueryViewSet(SearchMixin, ModelViewSet):
    queryset = ApplyQuery.objects.all()
    serializer_class = ApplyQuerySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):  # type: ignore
        actions = {
            "list": ApplyQuerySerializer,
            "retrieve": ApplyQueryFullSerializer,
        }
        return actions.get(self.action, self.serializer_class)

    def add_link_full_data(self, note_link: NoteLink):
        if self.apply_query:
            note_link.queries.add(self.apply_query)

    def save_note_link(self, source_data: dict, pre_link: dict):
        href = source_data.get('href')
        title = source_data.get('title')
        try:
            source_obj, _ = Source.objects.get_or_create(
                main_url=href, name=title)
        except Exception as e:
            source_obj = Source.objects\
                .filter(main_url=href, name=title)\
                .first()
        pre_link['source'] = source_obj.id
        note_link_serializer = NoteLinkSerializer(data=pre_link)
        note_link_serializer.is_valid(raise_exception=True)
        note_link_obj = note_link_serializer.save()
        self.add_link_full_data(note_link_obj)

    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        import traceback
        from search.find_origin import FindOrigin
        from search.ai_clean.pre_classify import PreClassifier
        apply_query = self.get_object()
        self.apply_query = apply_query

        try:
            search_query_data = self.search_note_data(
                apply_query.search_query,
                from_date=apply_query.from_date,
                to_date=apply_query.to_date)

        except Exception as e:
            apply_query.add_errors(str(e))
            print(traceback.format_exc())
            raise ValidationError(str(e))

        all_errors = {}
        pk_int = int(pk)

        if feed := self.search_service.feed:
            apply_query.last_feed = feed

        if errors := self.search_service.errors:
            apply_query.add_errors(errors, save=False)
            all_errors['search_service'] = errors

        find_origin = FindOrigin()
        find_origin.find_sources_by_apply_query(apply_query)
        if find_origin.errors:
            apply_query.add_errors(find_origin.errors, save=False)
            all_errors['find_origin'] = find_origin.errors

        pre_classifier = PreClassifier()
        pre_classifier.pre_classify_notes(apply_query)
        if pre_classifier.errors:
            apply_query.add_errors(pre_classifier.errors, save=False)
            all_errors['pre_classifier'] = pre_classifier.errors

        note_links = NoteLink.objects\
            .filter(queries=apply_query)\
            .filter()\
            .prefetch_related('note_contents')

        search_query_data['note_links'] = NoteLinkFullSerializer(
            note_links, many=True).data

        for entry in search_query_data['note_links']:
            entry['apply_query'] = pk_int

        all_sources = SourceSerializer(Source.objects.all(), many=True)
        search_query_data['all_sources'] = all_sources.data

        if all_errors:
            search_query_data['errors'] = all_errors

        apply_query.save()

        return Response(search_query_data)
