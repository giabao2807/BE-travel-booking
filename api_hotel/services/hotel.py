from datetime import datetime
from typing import List, Dict, Optional

from django.db.models import Avg, Count, Min, Max, Q, Sum, QuerySet

from api_general.models import City
from api_general.services import Utils
from api_hotel.models import Hotel, Room
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
    def get_available_room_types(cls, hotel: Hotel, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """
        Get available room types

        @param hotel: (Hotel) hotel instance
        @param start_date: (datetime) start date want to filter in range
        @param end_date: (datetime) end date want to filter in range
        @return: A dict with key is room_type_id and value is available rooms amount
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
        available_room_types = dict()
        booked_room_amount_mapping = cls.get_booked_rooms_in_range(start_date, end_date, hotel.id)
        room_amount_mapping = cls.get_room_amount_mapping(hotel.id)

        for _room_type_id, _room_amount in room_amount_mapping.items():
            _room_type_id_str = str(_room_type_id)
            available_room_amount = Utils.safe_int(_room_amount)
            booked_room_amount = Utils.safe_int(booked_room_amount_mapping.get(_room_type_id, 0))
            if booked_room_amount:
                available_room_amount -= booked_room_amount

            available_room_types[_room_type_id_str] = available_room_amount

        return available_room_types

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
                     Q(booking_item__booking__status__in=valid_booking_status)
        if hotel_id:
            booking_ft &= Q(room_type__hotel_id=hotel_id)

        booked_room_amount_mapping = dict(Room.objects.filter(booking_ft)\
            .values("room_type_id")\
            .annotate(booked_room_amount=Sum("booking_item__quantity"))\
            .values_list("room_type_id", "booked_room_amount"))

        return booked_room_amount_mapping

    @classmethod
    def get_room_amount_mapping(cls, hotel_id: Optional[int] = None) -> Dict[int, int]:
        """
        Get room amount by room type

        @param hotel_id: (Optional[int]) the hotel_id of room types you want to filter
        @return: A dict
        Example:

        """
        room_ft = Q()
        if hotel_id:
            room_ft &= Q(room_type__hotel_id=hotel_id)
        room_amount_mapping = dict(
            Room.objects.filter(room_ft)
                .values("room_type_id")
                .annotate(total_room_amount=Count("id"))
                .values_list("room_type_id", "total_room_amount")
        )

        return room_amount_mapping
