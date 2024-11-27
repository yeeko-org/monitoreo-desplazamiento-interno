from rest_framework import viewsets, permissions
# from django_filters import FilterSet, NumberFilter
from django.db.models import Count
# from rest_framework.decorators import action
# from rest_framework.response import Response

# from source.models import Source
from news.models import Source
from category.models import StatusControl

from api.catalogs.serializers import (
    SourceSerializer,
    StatusControlSerializer,
)
from .all import CatalogsView  # noqa
# from ..common_views import BaseViewSet, BaseStatusViewSet
# from ..space_time import ListSetMixin


class SourceViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class StatusControlViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = StatusControl.objects.all()
    serializer_class = StatusControlSerializer
