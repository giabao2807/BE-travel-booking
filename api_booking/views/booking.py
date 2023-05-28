from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_booking.models import Booking
from api_booking.serializers import BookingSerializer, CUBookingSerializer, ListBookingSerializer
from api_booking.services.booking import BookingService
from api_general.services import Utils
from api_general.services.vnpay import VNPayTransaction
from api_user.models import Profile
from api_user.permission import UserPermission
from api_user.statics import RoleData
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class BookingViewSet(BaseViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "payment_callback": []
    }
    serializer_map = {
        "retrieve": ListBookingSerializer,
        "list": ListBookingSerializer,
        "validate": CUBookingSerializer,
        "create": CUBookingSerializer,
    }

    def list(self, request, *args, **kwargs):
        self.queryset = Booking.objects.filter(customer=request.user)

        return super().list(request, *args, **kwargs)

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
        bank_code = request_body.get("bank_code")
        request_body["customer"] = request.user.id
        client_ip = Utils.get_client_ip(request)

        serializer = self.get_serializer(data=request_body)
        if bank_code and client_ip and serializer.is_valid(raise_exception=True):
            booking = serializer.save()
            payment_link = BookingService.create_payment_link(booking, bank_code, client_ip)
            print(payment_link)

            return Response({"payment_link": payment_link}, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=[HttpMethod.POST, HttpMethod.PUT, HttpMethod.GET])
    def payment_callback(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        booking_id = query_params.get("vnp_TxnRef")

        if VNPayTransaction.validate_response(query_params):
            BookingService.set_paid_booking(booking_id)
            return Response(dict(message="Changed the booking status to PAID"), status=status.HTTP_200_OK)
        else:
            return Response(dict(message="Invalid transaction"), status=status.HTTP_400_BAD_REQUEST)
