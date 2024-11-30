from rest_framework import serializers

from news.models import SearchQuery, ApplyQuery


class SearchQuerySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # save m2m fields
        instance = super().create(validated_data)

        # recalculate query white m2m fields
        instance.save(do_words=True)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save(do_words=True)
        return instance

    class Meta:
        model = SearchQuery
        fields = '__all__'


class WhenSerializer(serializers.Serializer):
    when = serializers.CharField(
        max_length=10, allow_blank=True, allow_null=True)
    from_date = serializers.DateField(allow_null=True)
    to_date = serializers.DateField(allow_null=True)


class ApplyQuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplyQuery
        fields = '__all__'
