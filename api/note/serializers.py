from rest_framework import serializers

from source.models import Source, SourceMethod
from note.models import NoteContent, NoteLink
# from api.catalogs.serializers import SourceSerializer


class BasicNoteContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteContent
        fields = "__all__"


class SourceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class NoteLinkFullSerializer(serializers.ModelSerializer):
    note_contents = BasicNoteContentSerializer(many=True, read_only=True)
    # source = SourceSimpleSerializer(read_only=True)

    class Meta:
        model = NoteLink
        fields = "__all__"


class NoteLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteLink
        fields = "__all__"


class NoteLinkSpecialSerializer(serializers.ModelSerializer):
    # is_dfi = serializers.BooleanField(allow_null=True)

    class Meta:
        model = NoteLink
        # read_only_fields = ["gnews_url", "source", "title"]
        # exclude = ["gnews_url", "title"]
        fields = "__all__"


class SourceMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceMethod
        fields = "__all__"


class NoteLinkAndContentSerializer(BasicNoteContentSerializer):
    note_link = NoteLinkSerializer()
    source_method = SourceMethodSerializer()
