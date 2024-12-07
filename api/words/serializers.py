from rest_framework import serializers

from search.models import WordList


class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordList
        fields = '__all__'
