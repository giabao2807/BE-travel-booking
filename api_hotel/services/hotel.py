from datetime import datetime
from typing import List, Dict, Optional

from django.db.models import Avg, Count, Min, Max, Q, Sum, QuerySet, F

from api_general.consts import DatetimeFormatter
from api_general.models import City, Coupon
from api_general.services import Utils, CityService
from api_hotel.models import Hotel, Room, HotelCoupon
from api_hotel.serializers import AvailableRoomSerializer
from base.query import GroupConcat
from common.constants.api_booking import BookingStatus


class HotelService:
    @classmethod
    def get_top_recommend_cities(cls, amount: int = 5) -> List[Dict[int, str]]:
        """
        Get top of recommend cities by rating
        @param amount: (int) Number of recommend cities
        @return: List of recommend cities
        Example:
        [
            {'id': 21, 'name': 'Hà Giang'},
            {'id': 22, 'name': 'Hà Nam'},
            {'id': 23, 'name': 'Hà Tĩnh'},
            {'id': 36, 'name': 'Lào Cai'},
            {'id': 46, 'name': 'Quảng Nam'}
        ]
        """
        top_cities = list(Hotel.objects.values("city_id") \
                          .annotate(avg_rate=Avg("hotel_reviews__rate"), total_rate=Count("*")) \
                          .filter(total_rate__gte=10) \
                          .order_by("-avg_rate") \
                          .values_list("city_id", flat=True)[:amount])
        city_values = list(City.objects.filter(id__in=top_cities) \
                           .annotate(total_hotel=Count('hotel__id')) \
                           .annotate(image=F('city_images__image__link')) \
                           .order_by("-total_hotel") \
                           .values("id", "name", "image"))

        return city_values

    @classmethod
    def get_hotel_cards(cls, hotel_ids: List[int]):
        hotel_card_values = Hotel.objects.filter(id__in=hotel_ids)\
            .values("id")\
            .annotate(
                rate_average=Avg("hotel_reviews__rate"),
                min_price=Min("rooms__price"),
                max_price=Max("rooms__price"),
                num_review=Count("hotel_reviews__id")
            )\
            .values("id", "name", "cover_picture", "address",
                    "rate_average", "min_price", "max_price", "num_review")

        return hotel_card_values

    @classmethod
    def get_available_rooms(cls, hotel: Hotel, start_date: datetime, end_date: datetime) -> List[dict]:
        """
        Get available room types

        @param hotel: (Hotel) hotel instance
        @param start_date: (datetime) start date want to filter in range
        @param end_date: (datetime) end date want to filter in range
        @return: A dict with key is room_id and value is available rooms amount
        Example:

        """
        booked_room_amount_mapping = cls.get_booked_rooms_in_range(start_date, end_date, hotel.id)
        rooms: List[dict] = list(cls.get_room_amounts(hotel.id))

        for _room in rooms:
            _room_id = _room.get("id")
            _total_room_amount = _room.get("quantity", 0)

            available_room_amount = Utils.safe_int(_total_room_amount)
            booked_room_amount = Utils.safe_int(booked_room_amount_mapping.get(_room_id, 0))
            if booked_room_amount:
                available_room_amount -= booked_room_amount

            _room["available_room_amount"] = available_room_amount
            image_links = _room.get("list_images", "")
            _room["list_images"] = list(image_links.split(","))

        return rooms

    @classmethod
    def get_booked_rooms_in_range(cls, start_date: datetime, end_date: datetime, hotel_id: Optional[int] = None) -> Dict[int, int]:
        """
        Get the booked room amount in range

        @param start_date: datetime
        @param end_date: datetime
        @param hotel_id: hotel id of room types you want to filter with
        @return: A dict
        Example:

        """
        date_range = [start_date, end_date]
        valid_booking_status = [BookingStatus.PAID, BookingStatus.UNPAID]
        date_range_ft = Q(booking_item__booking__start_date__range=date_range) \
            | Q(booking_item__booking__end_date__range=date_range) \
            | Q(booking_item__booking__start_date__lt=start_date, booking_item__booking__end_date__gt=end_date)
        booking_ft = date_range_ft & \
            Q(booking_item__room__isnull=False) & \
            Q(booking_item__booking__status__in=valid_booking_status) & \
            Q(is_active=True)
        if hotel_id:
            booking_ft &= Q(hotel_id=hotel_id)

        booked_room_amount_mapping = dict(
            Room.objects.filter(booking_ft)
                .values("id")
                .annotate(booked_room_amount=Sum("booking_item__quantity"))
                .values_list("id", "booked_room_amount")
        )

        return booked_room_amount_mapping

    @classmethod
    def get_room_amounts(cls, hotel_id: Optional[int] = None) -> QuerySet:
        """
        Get room amount by room type

        @param hotel_id: (Optional[int]) the hotel_id of room types you want to filter
        @return: A QuerySet
        Example:

        """
        room_ft = Q(is_active=True)
        if hotel_id:
            room_ft &= Q(hotel_id=hotel_id)
        room_fields = AvailableRoomSerializer.MODEL_FIELDS

        rooms = Room.objects.filter(room_ft)\
            .values("id")\
            .annotate(list_images=GroupConcat("room_images__image__link"))\
            .annotate(available_room_amount=F('quantity')) \
            .values("list_images", "available_room_amount", *room_fields)

        print(Utils.get_raw_query(rooms))
        return rooms

    @classmethod
    def get_current_coupon(cls, hotel_id: str) -> Coupon:
        current_date = datetime.now().date()
        base_ft = Q(
            is_active=True,
            start_date__date__lte=current_date,
            end_date__date__gte=current_date
        )
        for_all_coupon_ft = Q(for_all=True)
        selected_hotels_coupon_ft = Q(for_all=False, hotel_coupons__hotel_id=hotel_id)
        hotel_coupon_ft = base_ft & (for_all_coupon_ft | selected_hotels_coupon_ft)
        coupon = Coupon.objects.filter(hotel_coupon_ft).order_by("-discount_percent").first()

        return coupon

    @classmethod
    def get_filter_query(cls, request):
        city_id = request.query_params.get("city_id", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        start_date = Utils.safe_str_to_date(start_date, DatetimeFormatter.YYMMDD)
        end_date = Utils.safe_str_to_date(end_date, DatetimeFormatter.YYMMDD)

        top_hotel_ids = Hotel.objects.all() \
                             .values("id") \
                             .annotate(avg_rate=Avg("hotel_reviews__rate")) \
                             .order_by("-avg_rate") \
                             .values_list("id", flat=True)
        if city_id:
            city = City.objects.filter(id=city_id).first()
            top_hotel_ids = CityService.get_top_hotel_id_queryset(city)

        list_rs_hotel_id = []

        for hotel_id in top_hotel_ids:
            hotel = Hotel.objects.filter(id=hotel_id).first()
            is_available_room = True
            if start_date and end_date:
                is_available_room = HotelService.check_available_rooms(hotel, start_date, end_date)
            if is_available_room:
                list_rs_hotel_id.append(hotel_id)
        return list_rs_hotel_id

    @classmethod
    def check_available_rooms(cls, hotel: Hotel, start_date: datetime, end_date: datetime) -> bool:
        """
        Check available room types

        @param hotel: (Hotel) hotel instance
        @param start_date: (datetime) start date want to filter in range
        @param end_date: (datetime) end date want to filter in range
        @return: boolean
        Example:

        """
        booked_room_amount_mapping = cls.get_booked_rooms_in_range(start_date, end_date, hotel.id)
        rooms: List[dict] = list(cls.get_room_amounts(hotel.id))

        for _room in rooms:
            _room_id = _room.get("id")
            _total_room_amount = _room.get("quantity", 0)

            available_room_amount = Utils.safe_int(_total_room_amount)
            booked_room_amount = Utils.safe_int(booked_room_amount_mapping.get(_room_id, 0))
            if booked_room_amount:
                available_room_amount -= booked_room_amount

            if available_room_amount > 0:
                return True

        return False
