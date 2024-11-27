from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.query_search.views import SearchQueryViewSet
from api.words.views import (
    MainGroupViewSet, ComplementaryGroupViewSet, NegativeGroupViewSet,
    ListWordsViewSet)
from api.auth.login_views import UserLoginAPIView

router = DefaultRouter()

router.register('search_query', SearchQueryViewSet)
router.register('list_words', ListWordsViewSet)
router.register('main_group', MainGroupViewSet)
router.register('complementary_group', ComplementaryGroupViewSet)
router.register('negative_group', NegativeGroupViewSet)
urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('catalogs/', include('api.catalogs.urls')),
    path('', include(router.urls)),
]
