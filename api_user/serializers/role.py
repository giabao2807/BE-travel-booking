from rest_framework.serializers import ModelSerializer

from api_user.models import Role


class RoleSerializer(ModelSerializer):

    class Meta:
        model = Role
        fields = "__all__"


class SortRoleSerializer(ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'name')
