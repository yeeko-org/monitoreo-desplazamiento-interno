from rest_framework import serializers

from geo.models import State, Municipality, Locality, Location


class StateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = '__all__'


class MunicipalityListSerializer(serializers.ModelSerializer):
    link = serializers.HyperlinkedIdentityField(
        view_name='space_time_municipality-detail',
        lookup_field='pk'
    )

    class Meta:
        model = Municipality
        fields = '__all__'


class MunicipalityRetrieveSerializer(MunicipalityListSerializer):
    localities = LocalitySerializer(many=True, read_only=True)

    class Meta:
        model = Municipality
        fields = '__all__'


class StateRetrieveSerializer(StateListSerializer):
    municipalities = MunicipalityListSerializer(many=True, read_only=True)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
