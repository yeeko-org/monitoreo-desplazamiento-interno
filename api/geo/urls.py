from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.geo.serializers import (
    StateListViewSet,
    MunicipalityListViewSet,
    LocalityListViewSet,
)

router = DefaultRouter()

router.register(r'state', StateListViewSet, basename='space_time_state')
router.register(
    r'municipality', MunicipalityListViewSet, basename='space_time_municipality')
router.register(r'locality', LocalityListViewSet, basename='space_time_locality')
# router.register(r'location', LocationListViewSet, basename='space_time_location')
urlpatterns = [
    path('', include(router.urls)),
]
