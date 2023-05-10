from datetime import datetime
from typing import List, Dict, Optional

from django.db.models import Avg, Count, Min, Max, Q, Sum, QuerySet

from api_general.models import City
from api_general.services import Utils
from api_hotel.models import Hotel, Room, RoomType
from api_hotel.serializers import AvailableRoomTypeSerializer
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
        city_values = list(City.objects.filter(id__in=top_cities).values("id", "name"))

        return city_values

    @classmethod
    def get_hotel_cards(cls, hotel_ids: List[int]):
        hotel_card_values = Hotel.objects.filter(id__in=hotel_ids)\
            .values("id")\
            .annotate(
                rate_average=Avg("hotel_reviews__rate"),
                min_price=Min("room_types__price"),
                max_price=Max("room_types__price"),
                num_review=Count("hotel_reviews__id")
            )\
            .values("id", "name", "cover_picture", "address",
                    "rate_average", "min_price", "max_price", "num_review")

        return hotel_card_values

    @classmethod
    def get_available_room_types(cls, hotel: Hotel, start_date: datetime, end_date: datetime) -> List[dict]:
        """
        Get available room types

        @param hotel: (Hotel) hotel instance
        @param start_date: (datetime) start date want to filter in range
        @param end_date: (datetime) end date want to filter in range
        @return: A dict with key is room_type_id and value is available rooms amount
        Example:

        """
        booked_room_amount_mapping = cls.get_booked_rooms_in_range(start_date, end_date, hotel.id)
        room_types: List[dict] = list(cls.get_room_amount_mapping(hotel.id))

        for _room_type in room_types:
            _room_type_id = _room_type.get("id")
            _total_room_amount = _room_type.get("total_room_amount", 0)

            available_room_amount = Utils.safe_int(_total_room_amount)
            booked_room_amount = Utils.safe_int(booked_room_amount_mapping.get(_room_type_id, 0))
            if booked_room_amount:
                available_room_amount -= booked_room_amount

            _room_type["available_room_amount"] = available_room_amount

        return room_types

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
            | Q(booking_item__booking__end_date__range=date_range)
        booking_ft = date_range_ft & \
            Q(booking_item__room__isnull=False) & \
            Q(booking_item__booking__status__in=valid_booking_status) & \
            Q(room_type__is_active=True)
        if hotel_id:
            booking_ft &= Q(room_type__hotel_id=hotel_id)

        booked_room_amount_mapping = dict(
            Room.objects.filter(booking_ft)
                .values("room_type_id")
                .annotate(booked_room_amount=Sum("booking_item__quantity"))
                .values_list("room_type_id", "booked_room_amount")
        )

        return booked_room_amount_mapping

    @classmethod
    def get_room_amount_mapping(cls, hotel_id: Optional[int] = None) -> QuerySet:
        """
        Get room amount by room type

        @param hotel_id: (Optional[int]) the hotel_id of room types you want to filter
        @return: A QuerySet
        Example:

        """
        room_ft = Q(is_active=True)
        if hotel_id:
            room_ft &= Q(hotel_id=hotel_id)
        room_type_fields = AvailableRoomTypeSerializer.MODEL_FIELDS

        room_types = RoomType.objects.filter(room_ft)\
            .values("id")\
            .annotate(total_room_amount=Count("rooms__id"))\
            .values("total_room_amount", *room_type_fields)

        return room_types

    @classmethod
    def get_all_available_room_types(cls, hotel_id: int) -> List[dict]:
        available_room_types = list(
            RoomType.objects.filter(hotel_id=hotel_id, is_active=True)
                .values(*AvailableRoomTypeSerializer.MODEL_FIELDS)
        )

        return available_room_types
