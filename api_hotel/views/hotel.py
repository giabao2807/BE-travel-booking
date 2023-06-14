from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_booking.serializers import BookingReviewSerializer
from api_booking.services import BookingReviewService
from api_general.consts import DatetimeFormatter
from api_general.services import Utils
from api_hotel.models import Hotel
from api_hotel.serializers import HotelSerializer, AvailableRoomSerializer, HotelReviewSerializer, HotelCardSerializer, \
    CUHotelSerializer, CURoomSerializer, HotelCouponSerializer
from api_hotel.serializers.hotel import PartnerHotelCardSerializer
from api_hotel.services import HotelService
from api_user.permission import UserPermission, PartnerPermission
from api_user.statics import RoleData
from base.exceptions import BoniException
from base.exceptions.base import ErrorType
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class HotelViewSet(BaseViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "list": [],
        "create": [PartnerPermission],
        "update": [PartnerPermission],
        "for_management": [PartnerPermission],
        "hotels_for_coupon": [PartnerPermission],
        "retrieve": [],
        "get_available_rooms": [],
        "get_reviews": [],
    }
    serializer_map = {
        "create": CUHotelSerializer,
        "update": CUHotelSerializer,
        "list": HotelCardSerializer,
        "for_management": PartnerHotelCardSerializer,
        "get_available_rooms": AvailableRoomSerializer,
        "get_reviews": HotelReviewSerializer,
        "create_rooms": CURoomSerializer,
    }

    def create(self, request, *args, **kwargs):
        data = request.data
        data["owner"] = request.user.id

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        data = request.data
        hotel = self.get_object()
        data["owner"] = request.user.id
        if hotel.owner != request.user:
            raise BoniException(ErrorType.GENERAL, ["Bạn không là chủ khách sạn này"])

        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        [hotel_id_queryset, _order_by] = HotelService.get_filter_query(request)
        paginated_hotel_ids = self.paginate_queryset(hotel_id_queryset)
        hotel_cards = HotelService.get_hotel_cards(paginated_hotel_ids, _order_by)
        data = self.get_serializer(hotel_cards, many=True).data
        return Response(self.get_paginated_response(data).data)

    @action(detail=False, methods=[HttpMethod.GET])
    def for_management(self, request, *args, **kwargs):
        order_by = "-created_at"
        queryset = Hotel.objects.all()
        if request.user.role.id.hex == RoleData.PARTNER.value.get('id'):
            queryset = queryset.filter(owner=request.user)
        hotel_id_queryset = queryset.values_list("id", flat=True).order_by(order_by)
        paginated_hotel_ids = self.paginate_queryset(hotel_id_queryset)
        hotel_cards = HotelService.get_hotel_cards(paginated_hotel_ids, order_by)
        data = self.get_serializer(hotel_cards, many=True).data
        return Response(self.get_paginated_response(data).data)

    @action(detail=False, methods=[HttpMethod.GET])
    def hotels_for_coupon(self, request, *args, **kwargs):
        order_by = "-created_at"
        hotel_queryset = Hotel.objects.filter(owner=request.user).order_by(order_by)
        data = HotelCouponSerializer(hotel_queryset, many=True).data
        return Response(data)

    @action(detail=True, methods=[HttpMethod.PUT])
    def deactivate(self, request, *args, **kwargs):
        hotel = self.get_object()
        user = request.user
        if HotelService.check_deactive_tour(hotel, user):
            hotel.is_active = False
            hotel.save()
            return Response({"message": "Vô hiệu hoá thành công khách sạn!"}, status=status.HTTP_200_OK)
        return Response({"message": "Khách sạn đang được book, không thể vô hiệu hoá"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=[HttpMethod.PUT])
    def activate(self, request, *args, **kwargs):
        hotel = self.get_object()
        hotel.is_active = True
        hotel.save()
        return Response({"message": "Kích hoạt hoá thành công khách sạn!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=[HttpMethod.GET], url_path="get_available_rooms")
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
            for _room in available_rooms:
                list_room_images = _room.get("list_images", "")
                if list_room_images:
                    _room["list_images"] = list_room_images.split(",")
        data = self.get_serializer(available_rooms, many=True).data

        return Response(data)

    @action(detail=True, methods=[HttpMethod.GET])
    def get_reviews(self, request, *args, **kwargs):
        """
        URL: api/v1/hotel/{hotel_id}/get_reviews/?page={int}&page_size={int}
        Method: {GET}
        Authentication: NoRequired

        @param request:
        params:
        - hotel_id: (str - UUID format)
        - page: (int) page number
        - page_size: (int) page size
        @param args:
        @param kwargs:
        @return:
        Example:
        {
        "links": {
            "previous": null,
            "next": "https://bonitravel.online/api/v1/hotel/2800076077e74363923b13bfa5acb1f0/get_reviews?page=2"
        },
        "current": 1,
        "pageSize": 12,
        "pageNumber": 18,
        "count": 214,
        "results": [
            {
                "id": "0db7893b-34ac-45d8-8e94-1c8f87ad2685",
                "createdAt": "2023-05-06T23:07:02.174953+07:00",
                "updatedAt": "2023-05-06T23:07:29.645367+07:00",
                "isActive": true,
                "title": "Kỷ niệm phú quốc",
                "content": "Gia đình tôi để nghĩ dưỡng tại ks quá tuyệt vời tất cả các dịch vụ, cám ơn bạn giao và bạn công ,bạn phước,bạn thiện đã rất tận tình , chu đáo, gia đình sẽ quay lại dịp nữa.hi vọng vẩn gặp lại các bạn tại đây,",
                "rate": 5.0,
                "hotel": "28000760-77e7-4363-923b-13bfa5acb1f0",
                "owner": {
                    "id": "0023482c-c1d3-4859-ac48-09a0a77841db",
                    "avatar": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Faenza-avatar-default-symbolic.svg/2048px-Faenza-avatar-default-symbolic.svg.png",
                    "name": "Minh tuấn"
                }
            },
            ...
        ]
        """
        hotel = self.get_object()
        hotel_review_by_booking = BookingReviewService.get_hotel_review(hotel)
        serializer_booking_review = BookingReviewSerializer(hotel_review_by_booking, many=True)

        queryset = hotel.hotel_reviews.all().prefetch_related("owner")
        serializer_hotel_review = self.get_serializer(queryset, many=True)
        serializer = serializer_booking_review.data + serializer_hotel_review.data

        page = self.paginate_queryset(serializer)
        data = self.get_paginated_response(page).data

        return Response(data)

    @action(detail=True, methods=[HttpMethod.POST])
    def create_rooms(self, request, *args, **kwargs):
        hotel = self.get_object()
        if hotel.owner != request.user:
            raise BoniException(ErrorType.INVALID, ["Hotel"])
        room_data = request.data
        room_data["hotel"] = hotel.id

        return super().create(request, *args, **kwargs)
