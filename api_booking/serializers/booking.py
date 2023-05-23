from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from api_booking.models import Booking
from api_booking.serializers import CUBookingItemSerializer
from api_booking.services.booking import BookingService
from api_hotel.services import HotelService


class BookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = "__all__"


class CUBookingSerializer(ModelSerializer):
    booking_items = CUBookingItemSerializer(required=True, many=True)
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

    def validate_booking_items(self, booking_items):
        if not booking_items:
            raise ValidationError("booking_items field must has value")

        return booking_items

    def create(self, validated_data):
        booking: Booking = BookingService.create(validated_data)

        return booking

    def validate(self, attrs):
        booking_items = attrs.get("booking_items", [])
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        for _booking_item in booking_items:
            room_id = _booking_item.get("room_id", "")
            tour_id = _booking_item.get("tour_id", "")
            quantity = _booking_item.get("quantity", 0)

            if room_id:
                BookingService.validate_room_booking(room_id, quantity, start_date, end_date, raise_exception=True)
            if tour_id:
                BookingService.validate_tour_booking(tour_id, quantity, raise_exception=True)

        return attrs
