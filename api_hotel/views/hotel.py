from typing import List

from rest_framework.decorators import action
from rest_framework.response import Response

from api_general.consts import DatetimeFormatter
from api_general.services import Utils
from api_hotel.models import Hotel
from api_hotel.serializers import HotelSerializer, AvailableRoomSerializer
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
        "get_available_rooms": []
    }
    serializer_map = {
        "get_available_rooms": AvailableRoomSerializer
    }

    @action(detail=True, methods=[HttpMethod.GET], url_path="get-available-rooms")
    def get_available_rooms(self, request, *args, **kwargs):
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
        [
            {
                "id": "0567a1d8-9e55-4f37-b48b-63583e553344",
                "name": "Superior Twin Room",
                "beds": "2 double beds",
                "adults": 2,
                "children": 3,
                "description": "<div class=\"ChildRoomsList-room-featurebucket ChildRoomsList-room-featurebucket-Benefits\"><span class=\"ChildRoomsList-room-bucketspan\">Your price includes:</span><div><div class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--green\" data-element-name=\"free-breakfast\" data-room-feature-type=\"0\" data-selenium=\"ChildRoomList-roomFeature\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Free breakfast for 2</span></span></span></div></div></div><div><div class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--green\" data-room-feature-type=\"0\" data-selenium=\"ChildRoomList-roomFeature\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Parking, Free WiFi, Free fitness center access</span></span></span></div></div></div><div><div aria-describedby=\"rc-tooltip-638\" class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--withHover ChildRoomsList-roomFeature--green\" data-room-feature-type=\"5\" data-selenium=\"ChildRoomList-roomFeature\" tabindex=\"0\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Extra low price! (non-refundable)</span><i class=\"ficon ficon-10 ficon-hover-details\"></i></span></span></div></div></div></div>",
                "price": 2496000,
                "square": "25 m²/269 ft²",
                "totalRoomAmount": 8,
                "availableRoomAmount": 8
            },
            {
                "id": "573bed90-dbe6-4812-ada0-a34922e36486",
                "name": "Deluxe Twin City View",
                "beds": "2 single beds",
                "adults": 4,
                "children": 1,
                "description": "<div class=\"ChildRoomsList-room-featurebucket ChildRoomsList-room-featurebucket-Benefits\"><span class=\"ChildRoomsList-room-bucketspan\">Your price includes:</span><div><div class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--green\" data-element-name=\"free-breakfast\" data-room-feature-type=\"0\" data-selenium=\"ChildRoomList-roomFeature\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Free breakfast for 2</span></span></span></div></div></div><div><div class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--green\" data-room-feature-type=\"0\" data-selenium=\"ChildRoomList-roomFeature\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Local breakfast, Vegetarian Breakfast, Parking, Car rental, Motorcycle rental, Bike rental, Hand sanitizer, Room sanitizing, Free Premium Wifi, Indoor gym access, Free pool access, Free fitness center access, Cable TV channels, Smart TV (with apps), Dumbbells, Treadmill</span></span></span></div></div></div><div><div class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--green\" data-room-feature-type=\"3\" data-selenium=\"ChildRoomList-roomFeature\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Pay at the hotel</span></span></span></div></div></div><div><div class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--green\" data-room-feature-type=\"0\" data-selenium=\"ChildRoomList-roomFeature\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Free Wi-Fi</span></span></span></div></div></div><div><div aria-describedby=\"rc-tooltip-602\" class=\"ChildRoomsList-roomFeature ChildRoomsList-roomFeature--withHover ChildRoomsList-roomFeature--green\" data-room-feature-type=\"5\" data-selenium=\"ChildRoomList-roomFeature\" tabindex=\"0\"><div data-element=\"room-feature\"><i class=\"RoomFeature__Icon ficon ficon-14 ficon-noti-check-mark-sharp\"></i><span class=\"RoomFeature__Title RoomFeature__Title--plain\"><span class=\"ChildRoomsList-roomFeature-TitleWrapper\"><span class=\"Spanstyled__SpanStyled-sc-16tp9kb-0 AeAps kite-js-Span\" data-element=\"room-feature-text\">Cancellation policy</span><i class=\"ficon ficon-10 ficon-hover-details\"></i></span></span></div></div></div></div>",
                "price": 2041667,
                "square": "25 m²/269 ft²",
                "totalRoomAmount": 7,
                "availableRoomAmount": 7
            }
        ]
        """
        params: dict = request.query_params.dict()
        start_date = params.get("start_date", "")
        end_date = params.get("end_date", "")
        start_date = Utils.safe_str_to_date(start_date, DatetimeFormatter.YYMMDD)
        end_date = Utils.safe_str_to_date(end_date, DatetimeFormatter.YYMMDD)
        hotel = self.get_object()

        if start_date and end_date:
            available_rooms = HotelService.get_available_rooms(hotel, start_date, end_date)
        else:
            available_rooms = HotelService.get_room_amounts(hotel.id)
        data = self.get_serializer(available_rooms, many=True).data

        return Response(data)
