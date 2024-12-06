from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter

from api.pagination import CustomPagination


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    # filterset_class = FilterSet
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    ordering_fields = ['name']


class BaseStatusViewSet(BaseViewSet):
    filterset_fields = ['status_validation']
    ordering_fields = ['name', 'count', 'status_validation__order']
