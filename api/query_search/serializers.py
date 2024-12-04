from rest_framework import serializers

from api.note.serializers import LinkSerializer
from news.models import Link, SearchQuery, ApplyQuery




class SearchQuerySerializer(serializers.ModelSerializer):

    links =  serializers.SerializerMethodField()

    def get_links(self, obj):
        return LinkSerializer(
            Link.objects.filter(queries__search_query__id=obj.id),
            many=True).data

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
        max_length=10, allow_blank=True, allow_null=True, required=False)
    from_date = serializers.DateField(allow_null=True)
    to_date = serializers.DateField(allow_null=True)


class ApplyQuerySerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplyQuery
        fields = '__all__'
