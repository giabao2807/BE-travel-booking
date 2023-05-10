from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from api_hotel.models import RoomType


class RoomTypeSerializer(ModelSerializer):

    class Meta:
        model = RoomType
        exclude = ['is_active', 'hotel']


class AvailableRoomTypeSerializer(Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=255)
    beds = serializers.CharField(max_length=255, allow_null=True)
    adults = serializers.IntegerField(allow_null=True)
    children = serializers.IntegerField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    price = serializers.IntegerField()
    square = serializers.CharField(allow_null=True)

    # extra fields:
    total_room_amount = serializers.IntegerField(allow_null=True)
    available_room_amount = serializers.IntegerField(allow_null=True)

    MODEL_FIELDS = [
        "id",
        "name",
        "beds",
        "adults",
        "children",
        "description",
        "price",
        "square",
    ]

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
