from django.urls import include, path


from rest_framework import routers

from api.catalogs.all import CatalogsView
from api.catalogs import ClusterViewSet, SourceViewSet
from api.words.views import WordListViewSet


router = routers.DefaultRouter()

router.register(r'source', SourceViewSet, basename='catalog_source')
router.register(r'cluster', ClusterViewSet, basename='catalog_cluster')
router.register(r'word_list', WordListViewSet, basename='catalog_word_list')


urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]
