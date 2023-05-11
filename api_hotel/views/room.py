from rest_framework.decorators import action
from rest_framework.response import Response

from api_hotel.models import Room
from api_hotel.serializers import RoomSerializer
from api_hotel.services import HotelService, RoomService
from api_user.permission import UserPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class RoomViewSet(BaseViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = []

    @action(detail=False, methods=[HttpMethod.GET], url_path="get_room_for_hotel")
    def get_room_for_hotel(self, request, *args, **kwargs):
        hotel_id = request.query_params.get("hotel_id", 5)
        room_ids = RoomService.get_room_ids_by_hotel(hotel_id)
        room_cards = RoomService.get_room_cards(room_ids)
        data = self.get_serializer(room_cards, many=True).data

        return Response(data)


