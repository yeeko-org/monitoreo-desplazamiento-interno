from rest_framework import serializers

from news.models import Source, Cluster, SourceOrigin, ValidOption
from category.models import StatusControl
from api.note.serializers import NoteLinkSerializer
from ps_schema.models import (Level, Collection, CollectionLink, FilterGroup)


class StatusControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusControl
        fields = "__all__"


class SourceOriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceOrigin
        fields = "__all__"


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class SourceCountSerializer(serializers.ModelSerializer):
    note_links_count = serializers.SerializerMethodField()

    def get_note_links_count(self, obj):
        return obj.note_links.count()

    class Meta:
        model = Source
        fields = "__all__"


class SourceFullSerializer(serializers.ModelSerializer):
    note_links = NoteLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Source
        fields = "__all__"


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = "__all__"


class ValidOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidOption
        fields = "__all__"


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"


class CollectionLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionLink
        fields = "__all__"


class FilterGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterGroup
        fields = "__all__"

