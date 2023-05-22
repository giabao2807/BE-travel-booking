from django.db.models import QuerySet, Avg

from api_general.models import City
from api_hotel.models import Hotel
from api_tour.models import Tour


class CityService:
    @classmethod
    def get_top_hotel_id_queryset(cls, city: City) -> QuerySet:
        hotel_queryset = Hotel.objects.filter(city=city) \
                             .values("id") \
                             .annotate(avg_rate=Avg("hotel_reviews__rate")) \
                             .order_by("-avg_rate") \
                             .values_list("id", flat=True)

        return hotel_queryset

    @classmethod
    def get_top_tour_queryset(cls, city: City) -> QuerySet:
        tour_queryset = Tour.objects.filter(city=city) \
                             .order_by("-rate")
        return tour_queryset
