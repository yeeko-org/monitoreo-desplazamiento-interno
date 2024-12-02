from rest_framework import viewsets, permissions
# from django_filters import FilterSet, NumberFilter
from django.db.models import Count
# from rest_framework.decorators import action
# from rest_framework.response import Response

# from source.models import Source
from news.models import Source, Cluster
from category.models import StatusControl

from api.catalogs.serializers import (
    SourceSerializer,
    StatusControlSerializer,
    ClusterSerializer,
)
from .all import CatalogsView  # noqa
# from ..common_views import BaseViewSet, BaseStatusViewSet
# from ..space_time import ListSetMixin


class SourceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


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


