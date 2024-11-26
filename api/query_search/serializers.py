from rest_framework import serializers

from news.models import SearchQuery


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = '__all__'
