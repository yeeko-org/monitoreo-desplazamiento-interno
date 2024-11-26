from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.words.serializers import MainGroupSerializer
from news.models import MainGroup, ComplementaryGroup, NegativeGroup


class MainGroupViewSet(ModelViewSet):
    queryset = MainGroup.objects.all()
    serializer_class = MainGroupSerializer
    permission_classes = [IsAuthenticated]


class ComplementaryGroupViewSet(ModelViewSet):
    queryset = ComplementaryGroup.objects.all()
    serializer_class = MainGroupSerializer
    permission_classes = [IsAuthenticated]


class NegativeGroupViewSet(ModelViewSet):
    queryset = NegativeGroup.objects.all()
    serializer_class = MainGroupSerializer
    permission_classes = [IsAuthenticated]
