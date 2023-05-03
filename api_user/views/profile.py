from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_user.models.profile import Profile
from api_user.permission import UserPermission
from api_user.serializers import ProfileDetailSerializer
from api_user.serializers.profile import MyProfileSerializer
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class ProfileViewSet(BaseViewSet):
    view_set_name = "profile"
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer
    serializer_map = {
        "infor": MyProfileSerializer
    }
    permission_classes = [UserPermission]

    @action(detail=False, methods=HttpMethod.GET)
    def info(self, request, *args, **kwargs):
        user = request.user
        serializer = MyProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
