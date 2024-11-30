from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.words.serializers import WordListSerializer
from news.models import WordList


class WordListViewSet(ModelViewSet):
    queryset = WordList.objects.all()
    serializer_class = WordListSerializer
    permission_classes = [IsAuthenticated]
