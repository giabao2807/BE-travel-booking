from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_booking.models import Booking
from api_booking.serializers import BookingSerializer, CUBookingSerializer
from api_booking.services.booking import BookingService
from api_general.services import Utils
from api_user.permission import UserPermission
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
        "validate": CUBookingSerializer,
        "create": CUBookingSerializer,
    }

    @action(detail=False, methods=[HttpMethod.POST])
    def validate(self, request, *args, **kwargs):
        request_body = request.data.dict()

        serializer = self.get_serializer(data=request_body)
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        request_body = request.data
        bank_code = request_body.get("bank_code")
        request_body["customer_id"] = request.user.id
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
        print(request.data)
        print(request.query_params)

        return Response(status=status.HTTP_204_NO_CONTENT)
