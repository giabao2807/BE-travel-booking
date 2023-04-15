from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_user.models import Profile
from api_user.serializers import ProfileDetailSerializer


class AccountGeneralInfo(ModelSerializer):
    profile = ProfileDetailSerializer()

    class Meta:
        model = Profile
        fields = ['id', 'email', 'avatar', 'role', 'profile']


class LoginAccountSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    class Meta:
        model = Profile
        fields = ["email", "password"]


class CreateProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['email', 'password', 'last_name', 'first_name', 'gender']
