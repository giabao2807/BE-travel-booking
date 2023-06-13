from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from api_hotel.models import Room, RoomImage
from api_hotel.services import RoomService


class RoomSerializer(ModelSerializer):

    class Meta:
        model = Room
        exclude = ['is_active', 'hotel', 'benefit']


class PartnerRoomHotelSerializer(ModelSerializer):

    class Meta:
        model = Room
        fields = ["id", "name",
                  "price", "square", "quantity"]


class CURoomSerializer(ModelSerializer):
    name = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
    beds = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
    price = serializers.IntegerField(required=True, allow_null=False)
    square = serializers.CharField(max_length=255, required=True, allow_null=False, allow_blank=False)
    room_images = serializers.ListField(child=serializers.FileField(), required=True, write_only=True)

    class Meta:
        model = Room
        fields = [
            "id", "name", "beds", "adults", "children", "description",
            "price", "square", "hotel", "quantity", "room_images"
        ]

    @transaction.atomic
    def create(self, validated_data):
        room_images = validated_data.pop("room_images", [])
        room = super().create(validated_data)
        RoomService.bulk_create_room_images(room_images, room.id)

        return room


class AvailableRoomSerializer(Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    beds = serializers.CharField(max_length=255, allow_null=True)
    adults = serializers.IntegerField(allow_null=True)
    children = serializers.IntegerField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    price = serializers.IntegerField()
    square = serializers.CharField(allow_null=True)
    quantity = serializers.IntegerField()

    # extra fields:
    available_room_amount = serializers.IntegerField(allow_null=True)
    list_images = serializers.ListField(required=False)

    MODEL_FIELDS = [
        "id",
        "name",
        "beds",
        "adults",
        "children",
        "description",
        "price",
        "square",
        "quantity"
    ]

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
