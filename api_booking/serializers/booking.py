from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from api_booking.models import Booking
from api_booking.serializers import CUBookingItemSerializer
from api_booking.services.booking import BookingService


class BookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = "__all__"


class CUBookingSerializer(ModelSerializer):
    booking_items = CUBookingItemSerializer(required=True)
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=True)

    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        if start_date > end_date:
            raise ValidationError("start_date must not greater than end_date")

        return attrs

    def create(self, validated_data):
        booking: Booking = BookingService.create(validated_data)

        return booking
