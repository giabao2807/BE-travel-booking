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

    def list(self, request, *args, **kwargs):
        """
        URL: api/v1/general/city
        Method: {GET}
        Authentication: NoRequired
        @param request:
        @param args:
        @param kwargs:
        @return: List of all cities
        Example:
        [
            {
                "id": 1, "createdAt": "2023-05-06T21:52:58.429543+07:00",
                "name": "An Giang", "zipcode": "880000",
                "country": "Việt Nam",
                "longitude": null,
                "latitude": null
            },
        ]
        """
        data = self.get_serializer(self.queryset, many=True).data
        return Response(data)

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
        """
        URL: api/v1/general/city/{id}/top-hotels/?page_size={int}&page={int}
        Method: {GET}
        Authentication: NoRequired
        @param request:
        - page_size(int - default is 12): Amount of records want to get each page
        - page(int - default is 1): Page number
        @param args:
        @param kwargs:
        @return: List of hotels by city
        Example:
        Request URL: http://localhost:8000/api/v1/general/city/21/top-hotels/?page_size=2&page=1
        {
            "links": {
                "previous": null,
                "next": "http://localhost:8000/api/v1/general/city/21/top-hotels/?page=2&page_size=2"
            },
            "current": 1,
            "pageSize": 2,
            "pageNumber": 2,
            "count": 3,
            "results": [
                {
                    "name": "Nhà Nghỉ Giang Sơn",
                    "address": "Km3, Group 1 Cau Me Village, Phuong Thien Ward, Hà Giang 310000 Việt Nam",
                    "priceRange": "",
                    "coverPicture": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/18/b1/6d/24/hien-khach-s-n.jpg?w=1200&h=-1&s=1",
                    "rateAverage": 5.0
                },
                {
                    "name": "H'Mong Village Resort",
                    "address": "Khu Tráng Kìm Xã Đông Hà, huyện Quản Bạ, Hà Giang 20000 Việt Nam",
                    "priceRange": "",
                    "coverPicture": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/28/6e/23/e3/h-mong-village-resort.jpg?w=1200&h=-1&s=1",
                    "rateAverage": 5.0
                }
            ]
        }
        """
        city = self.get_object()

        hotel_id_queryset = CityService.get_top_hotel_id_queryset(city)
        paginated_hotel_ids = self.paginate_queryset(hotel_id_queryset)
        hotel_cards = HotelService.get_hotel_cards(paginated_hotel_ids)
        data = self.get_serializer(hotel_cards, many=True).data

        return Response(self.get_paginated_response(data).data)

