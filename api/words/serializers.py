from rest_framework import serializers

from news.models import (
    MainGroup, ComplementaryGroup, NegativeGroup, WordList)


class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordList
        fields = '__all__'


class MainGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainGroup
        fields = '__all__'


class ComplementaryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplementaryGroup
        fields = '__all__'


class NegativeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegativeGroup
        fields = '__all__'
