
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


from api.catalogs.serializers import (
    SourceSerializer,
    StatusControlSerializer,
    LevelSerializer,
    CollectionSerializer,
    CollectionLinkSerializer,
    FilterGroupSerializer,
)
from news.models import Source
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
