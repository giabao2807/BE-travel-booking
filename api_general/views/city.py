from rest_framework.decorators import action
from rest_framework.response import Response

from api_general.models import City
from api_general.serializers import CitySerializer
from api_general.services import Utils
from api_hotel.services import HotelService
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class CityViewSet(BaseViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = []

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
