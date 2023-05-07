from typing import List, Dict
from django.db.models import Avg, Count, Min, Max, Value, CharField
from django.db.models.functions import Concat

from api_general.models import City
from api_hotel.models import Hotel


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
                max_price=Max("room_types__price")
            )\
            .values("id", "name", "cover_picture", "address", "rate_average", "min_price", "max_price")

        return hotel_card_values
