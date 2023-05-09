from rest_framework.decorators import action
from rest_framework.response import Response

from api_hotel.models import RoomType
from api_hotel.serializers import RoomTypeSerializer
from api_hotel.services import HotelService, RoomTypeService
from api_user.permission import UserPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class RoomTypeViewSet(BaseViewSet):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    permission_classes = []

    @action(detail=False, methods=[HttpMethod.GET], url_path="get_room_type_for_hotel")
    def get_room_type_for_hotel(self, request, *args, **kwargs):
        hotel_id = request.query_params.get("hotel_id", 5)
        room_type_ids = RoomTypeService.get_room_type_ids_by_hotel(hotel_id)
        room_type_cards = RoomTypeService.get_room_type_cards(room_type_ids)
        data = self.get_serializer(room_type_cards, many=True).data

        return Response(data)


