from rest_framework import serializers

from news.models import Note


class BasicNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = "__all__"


class NoteAndLinkSerializer(BasicNoteSerializer):
    link_pk = serializers.ReadOnlyField(source='link.pk')
    link_real_url = serializers.ReadOnlyField(source='link.real_url')
    link_published_at = serializers.ReadOnlyField(source='link.published_at')
    link_valid = serializers.ReadOnlyField(source='link.valid')
