from rest_framework.decorators import action

from api_tour.models import Tour
from api_tour.serializers import TourSerializer, CardTourSerializer
from api_tour.services import TourService
from api_tour.services.view import TourViewService
from api_user.permission import UserPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class TourViewSet(BaseViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "list": [],
        "retrieve": [],
        "filter_by_date_city": []
    }

    serializer_map = {
        'list': CardTourSerializer,
        'filter_by_date_city': CardTourSerializer,
    }

    @action(detail=False, methods=[HttpMethod.GET])
    def filter_by_date_city(self, request, *args, **kwargs):
        """
        URL: api/v1/city/filter_by_date_city/?start_date={date}&end_date={date}&city_id={id}
        Method: {GET}
        Authentication: NoRequired

        @param request:
        - start_date: date_str (format: "YYYY-MM-DD") start date want to filter
        - end_date: date_str (format: "YYYY-MM-DD") end date want to filter
        - city_id: int id of city want to filter
        - If start_date and end_date are None together -> Get all active tours
        @param args:
        @param kwargs:
        @return:
        Example:
        {
            "links": {
                "previous": null,
                "next": "http://localhost:8000/api/v1/tour/filter_by_date/?end_date=2023-04-04&page=2&start_date=2023-04-03"
            },
            "current": 1,
            "pageSize": 12,
            "pageNumber": 15,
            "count": 180,
            "results": [
                {
                    "id": "61746ee8-c335-4544-b70f-c39169605b18",
                    "name": "Tour Hà Giang 2 Ngày 3 Đêm: Cao Nguyên Đá Đồng Văn – Cột Cờ Lũng Cú – Sông Nho Quế",
                    "coverPicture": "https://www.vietnambooking.com/wp-content/uploads/2020/05/tour-ha-giang-2-ngay-3-dem-8-300x194.jpg",
                    "totalDays": "2 ngày 3 đêm",
                    "languageTour": "Việt Nam",
                    "price": 3486000,
                    "rate": 4.5,
                    "numReview": 106,
                    "city": "Hà Nội",
                    "departure": "Hà Nội, Hàng ngày",
                    "traffics": "['o_to', 'tau_thuy']"
                },
                ...
            ]
        }
        """
        request_params = request.query_params.dict()
        start_date = request_params.get("start_date", "")
        end_date = request_params.get("end_date", "")
        city_id = request_params.get("city_id", None)

        if start_date or end_date:
            start_date, end_date = TourViewService.validate_filter_by_date_params(start_date, end_date)
            tour_qs = TourService.filter_by_date(start_date, end_date)
        else:
            tour_qs = Tour.objects.filter(is_active=True).order_by("-updated_at")
        self.queryset = tour_qs.filter(city__id=city_id) if city_id else tour_qs

        return super().list(request, *args, **kwargs)
