from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from news.models import SearchQuery
from api.query_search.serializers import SearchQuerySerializer


class SearchQueryViewSet(ModelViewSet):
    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        search_query_obj = serializer.save()
        search_query_obj.save(do_words=True)
