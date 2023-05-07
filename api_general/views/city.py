from rest_framework.decorators import action
from rest_framework.response import Response

from api_general.models import City
from api_general.serializers import CitySerializer
from api_general.services import Utils, CityService
from api_hotel.serializers import HotelCardSerializer
from api_hotel.services import HotelService
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class CityViewSet(BaseViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = []
    serializer_map = {
        "top_hotels": HotelCardSerializer
    }

    @action(detail=False, methods=[HttpMethod.GET], url_path="top-recommend-cities")
    def top_recommend_cities(self, request, *args, **kwargs):
        """
        URL: api/v1/general/city/top-recommend-cities
        Method: {GET}
        Authentication: NoRequired
        @param request:
        - amount(int - default is 5): Amount of cities want to get
        @param args:
        @param kwargs:
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
        amount = Utils.safe_int(request.query_params.get("amount", 5))
        recommend_cities = HotelService.get_top_recommend_cities(amount)

        return Response(recommend_cities)

    @action(detail=True, methods=[HttpMethod.GET], url_path="top-hotels")
    def top_hotels(self, request, *args, **kwargs):
        city = self.get_object()

        hotel_id_queryset = CityService.get_top_hotel_id_queryset(city)
        paginated_hotel_ids = self.paginate_queryset(hotel_id_queryset)
        hotel_cards = HotelService.get_hotel_cards(paginated_hotel_ids)
        data = self.get_serializer(hotel_cards, many=True).data

        return Response(self.get_paginated_response(data).data)
