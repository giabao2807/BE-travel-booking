from rest_framework.serializers import ModelSerializer

from api_hotel.models import Hotel


class HotelSerializer(ModelSerializer):

    class Meta:
        model = Hotel
        fields = "__all__"
