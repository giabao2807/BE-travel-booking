import os

from django.contrib.auth.hashers import check_password, make_password
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_user.models.profile import Profile
from api_user.permission import UserPermission, AdminPermission
from api_user.serializers import ProfileDetailSerializer, CreateProfileSerializer
from api_user.serializers.profile import BasicProfileSerializer, AdminProfileSerializer, AdminCreatePartnerSerializer, \
    PartnerSortSerializer
from api_user.services import ProfileService
from base.services import CloudinaryService
from base.views import BaseViewSet
from common.constants.base import HttpMethod, ErrorResponse, ErrorResponseType

load_dotenv()


class ProfileViewSet(BaseViewSet):
    view_set_name = "profile"
    queryset = Profile.objects.all()
    serializer_class = ProfileDetailSerializer
    serializer_map = {
        "infor": BasicProfileSerializer,
        "list": AdminProfileSerializer,
        "create": AdminCreatePartnerSerializer,
    }
    permission_classes = [UserPermission]

    permission_map = {
        "list": [AdminPermission],
        "list_partner": [AdminPermission],
        "create": [AdminPermission],
    }

    @action(detail=False, methods=[HttpMethod.GET])
    def list_partner(self, request, *args, **kwargs):
        self.queryset = ProfileService.list_partner()
        self.serializer_class = PartnerSortSerializer
        return super().list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = ProfileService.get_filter_query(request)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = ProfileService.create_partner(serializer.validated_data)
            if user:
                return Response({"message": "Tạo thành công đối tác mới!"}, status=status.HTTP_200_OK)
            else:
                return ErrorResponse(ErrorResponseType.CANT_CREATE, params=["partner"])

    @action(detail=False, methods=[HttpMethod.GET])
    def info(self, request, *args, **kwargs):
        user = request.user
        serializer = BasicProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = request.user
        avatar = request.FILES.get('avatar')
        if avatar:
            avatar_link = CloudinaryService.upload_image(avatar, os.getenv('CLOUDINARY_AVATAR_FOLDER'))
            request.data['avatar'] = avatar_link
        serializer = BasicProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=[HttpMethod.PATCH])
    def change_password(self, request, *args, **kwargs):
        account = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if check_password(old_password, account.password):
            account.password = make_password(new_password)
            account.save()
            return Response({"detail": "Changed password!"}, status=status.HTTP_200_OK)
        return Response({"error_message": "Old password is incorrect!"}, status=status.HTTP_400_BAD_REQUEST)
