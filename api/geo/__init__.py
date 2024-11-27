from rest_framework import viewsets, permissions

from api.pagination import CustomPagination
from geo.models import (
    State,
    Municipality,
    Locality,
    Location,)

from api.geo.serializers import (
    MunicipalityRetrieveSerializer,
    StateListSerializer,
    MunicipalityListSerializer,
    LocalitySerializer,
    LocationSerializer,
    StateRetrieveSerializer,)
# from ..common_views import BaseViewSet, BaseStatusViewSet


class ListSetMixin(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination


class StateListViewSet(ListSetMixin):
    queryset = State.objects.all().prefetch_related('municipalities')
    serializer_class = StateListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StateRetrieveSerializer
        return self.serializer_class


class MunicipalityListViewSet(ListSetMixin):
    queryset = Municipality.objects.all().prefetch_related('localities')
    serializer_class = MunicipalityListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MunicipalityRetrieveSerializer
        return self.serializer_class


class LocalityListViewSet(ListSetMixin):
    queryset = Locality.objects.all()
    serializer_class = LocalitySerializer


# class LocationViewSet(BaseViewSet):
#     queryset = Location.objects.all().exclude(
#         project__isnull=True, event__isnull=True)
#     serializer_class = LocationSerializer
#
#     filterset_fields = ['status_location']

