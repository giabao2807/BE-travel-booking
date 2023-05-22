from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer

from api_booking.models import BookingItem
from api_booking.services.booking import BookingService


class BookingItemSerializer(ModelSerializer):

    class Meta:
        model = BookingItem
        fields = "__all__"


class CUBookingItemSerializer(ModelSerializer):
    tour_id = serializers.UUIDField(required=False)
    room_id = serializers.UUIDField(required=False)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        model = BookingItem
        fields = ("tour_id", "room_id", "quantity")

    def validate(self, attrs):
        data = super().validate(attrs)
        tour_id = data.get("tour_id", "")
        room_id = data.get("room_id", "")

        if not any([tour_id, room_id]):
            raise ValidationError("must have tour_id or room_id value")
        if all([tour_id, room_id]):
            raise ValidationError("tour_id and room_id have value in the same time")

        return attrs
