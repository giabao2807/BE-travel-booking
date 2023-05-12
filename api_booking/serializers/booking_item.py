from rest_framework.serializers import ModelSerializer, Serializer

from api_booking.models import BookingItem


class BookingItemSerializer(ModelSerializer):

    class Meta:
        model = BookingItem
        fields = "__all__"


class CUBookingItemSerializer(Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        model = BookingItem
        fields = ("tour", "room", "quantity")
