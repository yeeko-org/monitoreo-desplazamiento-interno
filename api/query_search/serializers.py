from rest_framework import serializers

from news.models import SearchQuery


class SearchQuerySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.save(do_words=True)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save(do_words=True)
        return instance

    class Meta:
        model = SearchQuery
        fields = '__all__'
