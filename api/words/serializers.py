from rest_framework import serializers

from news.models import WordList


class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordList
        fields = '__all__'
