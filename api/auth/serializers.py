from rest_framework import serializers
# from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
# from classify_task.models import UserProfile
from profile_auth.models import User


class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    password = serializers.CharField(
        min_length=8,
        style={'input_type': 'password'})
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())])
    checkCondiction = serializers.BooleanField(
        required=False)
    key = serializers.CharField(required=False)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(
        required=True, style={'input_type': 'password'})
    key = serializers.CharField(required=False)


class UserDataSerializer(serializers.ModelSerializer):
    fullname = serializers.ReadOnlyField(source="full_name")
    token = serializers.ReadOnlyField(source="auth_token.key")

    class Meta(object):
        model = User
        fields = [
            "id", 'email', 'username', "first_name", "last_name",
            "token", "fullname"]


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "is_staff",
            "first_name",
            "last_name",
        ]
