from rest_framework import serializers

from news.models import Note, Link, SourceMethod
from api.catalogs.serializers import SourceSerializer


class BasicNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"


class LinkFullSerializer(serializers.ModelSerializer):
    notes = BasicNoteSerializer(many=True)
    source = SourceSerializer()

    class Meta:
        model = Link
        fields = "__all__"


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = "__all__"


class LinkSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["pk", "real_url", "is_dfi"]


class SourceMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceMethod
        fields = "__all__"


class NoteAndLinkSerializer(BasicNoteSerializer):
    # link_pk = serializers.ReadOnlyField(source='link.pk')
    # link_real_url = serializers.ReadOnlyField(source='link.real_url')
    # link_published_at = serializers.ReadOnlyField(source='link.published_at')
    # link_valid = serializers.ReadOnlyField(source='link.valid')
    link = LinkSerializer()
    source_method = SourceMethodSerializer()
