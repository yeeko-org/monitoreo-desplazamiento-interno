from django.urls import include, path


from rest_framework import routers

from api.catalogs.all import CatalogsView


router = routers.DefaultRouter()

# router.register(r'source', SourceViewSet, basename='catalog_source')


urlpatterns = [
    path("all/", CatalogsView.as_view(), name="catalogs_all"),
    path('', include(router.urls)),
]
