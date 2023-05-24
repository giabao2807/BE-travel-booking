from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_booking.models import Booking
from api_booking.serializers import BookingSerializer, CUBookingSerializer
from api_user.permission import UserPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class BookingViewSet(BaseViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [UserPermission]

    permission_map = {
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
        request_body["customer_id"] = request.user.id

        serializer = self.get_serializer(data=request_body)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response({"message": "Created success"}, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
