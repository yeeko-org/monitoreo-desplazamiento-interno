from rest_framework import viewsets, permissions
# from django_filters import FilterSet, NumberFilter
from django.db.models import Count
# from rest_framework.decorators import action
# from rest_framework.response import Response
from api.common_views import BaseViewSet

# from source.models import Source
from news.models import Source, Cluster, SourceOrigin
from category.models import StatusControl

from api.catalogs.serializers import (
    SourceSerializer,
    SourceFullSerializer,
    SourceCountSerializer,
    SourceOriginSerializer,
    StatusControlSerializer,
    ClusterSerializer,
)
from .all import CatalogsView  # noqa
# from ..common_views import BaseViewSet, BaseStatusViewSet
# from ..space_time import ListSetMixin


class SourceOriginViewSet(BaseViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SourceOrigin.objects.all()
    serializer_class = SourceOriginSerializer


class SourceViewSet(BaseViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Source.objects.all()\
        .prefetch_related('note_links')
    serializer_class = SourceCountSerializer

    def get_serializer_class(self):
        action_serializer = {
            'retrieve': SourceFullSerializer,
        }
        return action_serializer.get(self.action, self.serializer_class)


class StatusControlViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StatusControl.objects.all()
    serializer_class = StatusControlSerializer


class ClusterViewSet(viewsets.ModelViewSet):

    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    # filter_class = ClusterFilter
    # search_fields = ['name', 'description']
    # ordering_fields = ['name', 'description']


