from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.words.serializers import (
    MainGroupSerializer, ComplementaryGroupSerializer, NegativeGroupSerializer,
    WordListSerializer)
from news.models import (
    MainGroup, ComplementaryGroup, NegativeGroup, WordList)


class WordListViewSet(ModelViewSet):
    queryset = WordList.objects.all()
    serializer_class = WordListSerializer
    permission_classes = [IsAuthenticated]


class MainGroupViewSet(ModelViewSet):
    queryset = MainGroup.objects.all()
    serializer_class = MainGroupSerializer
    permission_classes = [IsAuthenticated]


class ComplementaryGroupViewSet(ModelViewSet):
    queryset = ComplementaryGroup.objects.all()
    serializer_class = ComplementaryGroupSerializer
    permission_classes = [IsAuthenticated]


class NegativeGroupViewSet(ModelViewSet):
    queryset = NegativeGroup.objects.all()
    serializer_class = NegativeGroupSerializer
    permission_classes = [IsAuthenticated]
