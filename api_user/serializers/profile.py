from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from api_user.models.profile import Profile


class ProfileDetailSerializer(ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['password', 'active']


class ProfileRegisterSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    avatar = serializers.CharField(required=False)

    def validate_email(self, value):
        duplicated_email = Account.objects.by_email(value)
        if duplicated_email is not None:
            raise ValidationError("Email already exists.")
        return value

    class Meta:
        model = Profile
        fields = ('id', 'last_name', 'first_name', 'gender', 'email', 'password', 'avatar')
