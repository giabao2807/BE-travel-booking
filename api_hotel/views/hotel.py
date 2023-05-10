from rest_framework.decorators import action
from rest_framework.response import Response

from api_general.consts import DatetimeFormatter
from api_general.services import Utils
from api_hotel.models import Hotel
from api_hotel.serializers import HotelSerializer
from api_hotel.services import HotelService
from api_user.permission import UserPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class HotelViewSet(BaseViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "list": [],
        "retrieve": [],
        "get_available_room_types": []
    }

    @action(detail=True, methods=[HttpMethod.GET], url_path="get-available-room-types")
    def get_available_room_types(self, request, *args, **kwargs):
        """
        URL: api/v1/hotel/{hotel_id}/get-available-room-types/?start_date={date}&end_date={date}
        Method: {GET}
        Authentication: NoRequired
        @param request:
        - hotel_id: (str) Hotel id
        - start_date: date_str (format: "YYYY-MM-DD") start date want to filter
        - end_date: date_str (format: "YYYY-MM-DD") end date want to filter
        @param args:
        @param kwargs:
        @return: List of available room types amount
        Example:
        {
            "0567a1d8-9e55-4f37-b48b-63583e553344": 8,
            "573bed90-dbe6-4812-ada0-a34922e36486": 7,
            "638c149e-72e4-4b8d-a10c-370db4f210de": 1,
            "801acbfd-b879-48ee-865a-3c392e470490": 3,
            "861ff75c-d35e-4676-9f2b-19c3989a9592": 7,
            "9b2f583d-98d8-4b6a-8f6f-c246067d0c19": 3,
            "b1f32828-0d9c-4ce0-8869-62730958989e": 3,
            "c096d852-7999-4353-ba3b-3b2ce7ac77a1": 8,
            "c5fe1c15-27f4-4217-91ef-c962cda53c64": 6,
            "fdc2508a-4d62-48bc-b0b9-28eeef7e10bd": 4
        }
        """
        params: dict = request.query_params.dict()
        start_date = params.get("start_date", "")
        end_date = params.get("end_date", "")
        start_date = Utils.safe_str_to_date(start_date, DatetimeFormatter.YYMMDD)
        end_date = Utils.safe_str_to_date(end_date, DatetimeFormatter.YYMMDD)
        hotel = self.get_object()
        available_room_types = dict()

        if start_date and end_date:
            available_room_types = HotelService.get_available_room_types(hotel, start_date, end_date)

        return Response(available_room_types)
