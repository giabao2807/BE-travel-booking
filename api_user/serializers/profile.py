from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_user.models.profile import Profile
from api_user.serializers.role import SortRoleSerializer


class PartnerSortSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['email', 'id', 'last_name', 'first_name']


class AdminCreatePartnerSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = ['email', 'last_name', 'first_name', 'address', 'phone']


class ProfileDetailSerializer(ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['password', 'is_active']


class AdminProfileSerializer(ModelSerializer):
    role = SortRoleSerializer()

    class Meta:
        model = Profile
        exclude = ('password', 'longitude', 'latitude', 'last_login')


class BasicProfileSerializer(ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = Profile
        exclude = ['password', "longitude", "latitude", 'role', 'is_active']


class ProfileRegisterSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    avatar = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ('id', 'last_name', 'first_name', 'gender', 'email', 'password', 'avatar')
