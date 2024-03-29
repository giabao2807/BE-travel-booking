from django.db.models import Q, Value
from django.db.models.functions import Collate
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_booking.consts import BookingType
from api_booking.models import Booking
from api_booking.serializers import BookingSerializer, CUBookingSerializer, ListBookingSerializer, \
    ListHotelBookingSerializer
from api_booking.serializers.booking import ListTourBookingSerializer, PartnerHotelBookingSerializer, \
    PartnerTourBookingSerializer
from api_booking.services.booking import BookingService
from api_general.services import Utils
from api_general.services.vnpay import VNPayTransaction
from api_user.models import Profile
from api_user.permission import UserPermission, PartnerPermission
from api_user.statics import RoleData
from base.exceptions import BoniException
from base.exceptions.base import ErrorType
from base.views import BaseViewSet
from common.constants.api_booking import BookingStatus
from common.constants.base import HttpMethod
from common.constants.base_const import SupportEnv


class BookingViewSet(BaseViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "payment_callback": [],
        "for_partner": [PartnerPermission]
    }
    serializer_map = {
        "retrieve": ListBookingSerializer,
        "validate": CUBookingSerializer,
        "create": CUBookingSerializer,
    }
    ignore_serializer_map_actions = ["list", "for_partner"]

    def list(self, request, *args, **kwargs):
        _type = request.query_params.get("type")
        _type = Utils.safe_int(_type)

        booking_ft = Q(customer=request.user)
        if _type:
            booking_ft = Q(type=_type) & Q(customer=request.user)
            self.serializer_class = ListHotelBookingSerializer if _type == BookingType.HOTEL else ListTourBookingSerializer
        else:
            self.serializer_class = ListBookingSerializer
        self.queryset = Booking.objects.filter(booking_ft).order_by("-created_at")

        return self._list(request, *args, **kwargs)

    def _list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        booking = self.get_object()
        user: Profile = request.user
        if user.role_id == RoleData.ADMIN.id or booking.customer == user:
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(dict(message="Invalid booking!"), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=[HttpMethod.POST])
    def validate(self, request, *args, **kwargs):
        request_body = request.data.dict()

        serializer = self.get_serializer(data=request_body)
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        request_body = request.data
        env = request.query_params.get("env")
        env = Utils.safe_int(env, SupportEnv.PROD)
        bank_code = request_body.get("bank_code")
        request_body["customer"] = request.user.id
        client_ip = Utils.get_client_ip(request)

        serializer = self.get_serializer(data=request_body)
        if bank_code and client_ip and serializer.is_valid(raise_exception=True):
            booking = serializer.save()
            payment_link = BookingService.create_payment_link(booking, bank_code, client_ip, env)
            print(payment_link)

            return Response({"payment_link": payment_link}, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=[HttpMethod.POST, HttpMethod.PUT, HttpMethod.GET])
    def payment_callback(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        booking_id = query_params.get("vnp_TxnRef")
        vnp_response_code = query_params.get("vnp_ResponseCode", "01")

        if VNPayTransaction.validate_response(query_params) and vnp_response_code == "00":
            BookingService.set_paid_booking(booking_id)
            BookingService.send_mail(booking_id)
            return Response(dict(message="Booking đã được thanh toán."), status=status.HTTP_200_OK)
        return Response(dict(message="Đã xảy ra lỗi khi thanh toán"), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=[HttpMethod.GET])
    def get_payment_link(self, request, *args, **kwargs):
        booking = self.get_object()
        bank_code = request.query_params.get("bank_code")
        env = request.query_params.get("env", SupportEnv.PROD)
        env = Utils.safe_int(env, SupportEnv.PROD)
        client_ip = Utils.get_client_ip(request)

        if booking.status != BookingStatus.UNPAID:
            raise BoniException(ErrorType.INVALID, ["booking status"])
        if not bank_code:
            raise BoniException(ErrorType.INVALID, ["bank_code"])
        if booking.customer != request.user:
            raise BoniException(ErrorType.INVALID, ["booking ID"])

        payment_link = BookingService.create_payment_link(booking, bank_code, client_ip, env)
        return Response(dict(payment_link=payment_link))

    @action(detail=False, methods=[HttpMethod.GET])
    def for_management(self, request, *args, **kwargs):
        booking_type = Utils.safe_int(request.query_params.get("type", None))
        name = request.query_params.get('name', "")
        _status = request.query_params.get('status', None)

        if not booking_type or booking_type not in BookingType.values:
            return Response({"error_message": "Thiếu type trong request params"}, status=status.HTTP_400_BAD_REQUEST)

        self.serializer_class = PartnerHotelBookingSerializer if booking_type == BookingType.HOTEL else PartnerTourBookingSerializer
        self.queryset = BookingService.get_bookings_qs_for_manage(request.user, booking_type, name, _status)
        return super().list(request, *args, **kwargs)
