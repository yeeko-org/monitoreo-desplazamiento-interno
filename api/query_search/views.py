from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
# from urllib.parse import unquote
from abc import ABC, abstractmethod
from news.models import ApplyQuery, Link, SearchQuery, Note, Source
from api.query_search.serializers import (
    ApplyQuerySerializer, SearchQuerySerializer, WhenSerializer)
from api.note.serializers import (
    LinkFullSerializer, LinkSerializer)
from api.catalogs.serializers import SourceSerializer
from typing import Optional


class SearchMixin:

    apply_query: Optional[ApplyQuery] = None

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
        built_links = []

        for entry in search_entries:

            def get_link_serializer(link_instance):
                if self.apply_query:
                    link_instance.queries.add(self.apply_query)
                serialized_link = LinkFullSerializer(link_instance).data
                built_links.append(serialized_link)

            gnews_url = entry.pop('link')
            link_obj = Link.objects.filter(gnews_url=gnews_url).first()
            if link_obj:
                get_link_serializer(link_obj)
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
                link_serializer = LinkSerializer(data=pre_link)
                link_serializer.is_valid(raise_exception=True)
                link_obj = link_serializer.save()
                get_link_serializer(link_obj)
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
                built_links.append(pre_link)

        search_count = len(built_links)
        return {
            'search_count': search_count,
            'links': built_links,
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
        search_query_data = self.search_data()
        for entry in search_query_data['links']:
            entry['apply_query'] = pk
        return Response(search_query_data)
