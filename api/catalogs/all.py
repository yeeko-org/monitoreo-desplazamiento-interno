
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from api.words.serializers import WordListSerializer
from api.query_search.serializers import SearchQuerySerializer


from api.catalogs.serializers import (
    SourceSerializer,
    ClusterSerializer,
    StatusControlSerializer,
    LevelSerializer,
    CollectionSerializer,
    CollectionLinkSerializer,
    FilterGroupSerializer,
    SourceOriginSerializer,
    ValidOptionSerializer,
)
from source.models import Source, SourceOrigin
from note.models import ValidOption
from search.models import Cluster, SearchQuery, WordList
from api.geo.serializers import StateListSerializer
from ps_schema.models import Level, Collection, CollectionLink, FilterGroup

from geo.models import State
from category.models import StatusControl


class CatalogsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):

        catalogs = {

            # "event_groups": EventGroupSerializer(
            #     EventGroup.objects.all(), many=True).data,
            # "event_types": EventTypeSerializer(
            #     EventType.objects.all(), many=True).data,
            # "event_subtypes": EventSubtypeSerializer(
            #     EventSubtype.objects.all(), many=True).data,
            # "involved_roles": InvolvedRoleSerializer(
            #     InvolvedRole.objects.all(), many=True).data,

            "sources": SourceSerializer(
                Source.objects.all(), many=True).data,
            "source_origins": SourceOriginSerializer(
                SourceOrigin.objects.all(), many=True).data,
            "clusters": ClusterSerializer(
                Cluster.objects.all(), many=True).data,
            "valid_options": ValidOptionSerializer(
                ValidOption.objects.all(), many=True).data,

            "word_lists": WordListSerializer(
                WordList.objects.all(), many=True).data,
            "search_queries": SearchQuerySerializer(
                SearchQuery.objects.all(), many=True).data,

            "status_control": StatusControlSerializer(
                StatusControl.objects.all(), many=True).data,
            "states": StateListSerializer(
                State.objects.all(), many=True).data,

            "levels": LevelSerializer(
                Level.objects.all(), many=True).data,
            "collections": CollectionSerializer(
                Collection.objects.all(), many=True).data,
            "collection_links": CollectionLinkSerializer(
                CollectionLink.objects.all(), many=True).data,
            "filter_groups": FilterGroupSerializer(
                FilterGroup.objects.all(), many=True).data,
        }
        return Response(catalogs)
