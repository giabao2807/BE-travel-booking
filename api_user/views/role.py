from api_user.permission import UserPermission
from base.views import BaseViewSet
from api_user.models import Role
from api_user.serializers import RoleSerializer


class RoleViewSet(BaseViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [UserPermission]
