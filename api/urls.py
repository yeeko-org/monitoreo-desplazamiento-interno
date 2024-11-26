from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.query_search.views import SearchQueryViewSet
from api.words.views import MainGroupViewSet, ComplementaryGroupViewSet, NegativeGroupViewSet

router = DefaultRouter()

router.register('search_query', SearchQueryViewSet)
router.register('main_group', MainGroupViewSet)
router.register('complementary_group', ComplementaryGroupViewSet)
router.register('negative_group', NegativeGroupViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
