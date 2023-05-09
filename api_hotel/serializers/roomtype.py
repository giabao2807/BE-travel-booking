from rest_framework.serializers import ModelSerializer

from api_hotel.models import RoomType


class RoomTypeSerializer(ModelSerializer):

    class Meta:
        model = RoomType
        exclude = ['is_active', 'hotel']
