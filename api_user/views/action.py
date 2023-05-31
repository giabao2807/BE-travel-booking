from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_user.models import Profile
from api_user.serializers import LoginAccountSerializer, ProfileDetailSerializer, CreateProfileSerializer
from api_user.services import TokenService, ProfileService
from base.utils import Utils
from common.constants.base import HttpMethod, ErrorResponse, ErrorResponseType
from base.views import BaseViewSet


class ActionViewSet(BaseViewSet):
    permission_classes = []
    view_set_name = "profile"
    queryset = Profile.objects.all().prefetch_related("roles")
    serializer_class = ProfileDetailSerializer
    serializer_map = {
        "login": LoginAccountSerializer,
        "sign_up": CreateProfileSerializer,
    }

    @action(detail=False, methods=[HttpMethod.POST])
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            login_data = ProfileService.login(serializer.validated_data)
            if login_data:
                return Response(login_data)
            else:
                return ErrorResponse(ErrorResponseType.GENERAL, params=["email/password invalid"])

    @action(detail=False, methods=[HttpMethod.POST])
    def sign_up(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = ProfileService.create_customer(serializer.validated_data)
            if user:
                resp = ProfileService.login_success_data(user)
                return Response(resp, status=status.HTTP_201_CREATED)
            else:
                return ErrorResponse(ErrorResponseType.CANT_CREATE, params=["user"])

    @action(detail=False, methods=[HttpMethod.GET])
    def refresh_new_token(self, request, *args, **kwargs):
        token = request.query_params.get("token", "")
        response_data = {}

        if token:
            response_data = TokenService.refresh_new_token(token)

        if response_data:
            return Response(response_data)
        else:
            return ErrorResponse(ErrorResponseType.INVALID, params=["token"])

    @action(methods=[HttpMethod.POST], detail=False)
    def forgot_password(self, request, *args, **kwargs):
        email = request.data.get('email')
        if email:
            profile = Profile.objects.by_email(email)
            if profile:
                password = Utils.gen_password()
                profile.password = make_password(password)
                profile.save()
                ProfileService.send_mail_reset_password(email=profile.email,
                                                        password=password, send_email=True)
                return Response({"success": "Reset password!"}, status=status.HTTP_200_OK)
        return Response({"error_message": "Email is incorrect!"}, status=status.HTTP_400_BAD_REQUEST)
