from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_booking.consts import BookingType
from api_booking.serializers import BookingReviewSerializer
from api_booking.services import BookingReviewService, FavoriteBookingService
from api_general.services import Utils
from api_tour.models import Tour
from api_tour.serializers import TourSerializer, CardTourSerializer
from api_tour.serializers.tour import CreateTourSerializer, TourCouponSerializer, CardFavoriteTourSerializer, \
    TourFavoriteInfoSerializer
from api_tour.services import TourService, TourImageService
from api_tour.services.view import TourViewService
from api_user.permission import UserPermission, PartnerPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod, ErrorResponse, ErrorResponseType


class TourViewSet(BaseViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "create": [PartnerPermission],
        "update": [PartnerPermission],
        "activate": [PartnerPermission],
        "list_tour": [PartnerPermission],
        "list": [],
        "retrieve": [],
        "filter_by_date_city": [],
        "get_reviews": [],
        "get_available_group_size": [],
        "top_tour": []
    }

    serializer_map = {
        'retrieve': TourFavoriteInfoSerializer,
        'create': CreateTourSerializer,
        'update': CreateTourSerializer,
        'list': CardFavoriteTourSerializer,
        'list_tour': CardTourSerializer,
        'top_tour': CardFavoriteTourSerializer,
        'recommend_for_user': CardFavoriteTourSerializer,
        'filter_by_date_city': CardFavoriteTourSerializer,
        'get_reviews': BookingReviewSerializer,
    }

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=[HttpMethod.POST])
    def add_favorite(self, request, *args, **kwargs):
        user = request.user
        tour = self.get_object()
        if FavoriteBookingService.add_favorite(tour=tour, user=user, _type=BookingType.TOUR):
            return Response({"message": "Đã thêm vào mục yêu thích!"})
        return Response({"message": "Đã tồn tại tour này ở mục yêu thích!"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=[HttpMethod.DELETE])
    def remove_favorite(self, request, *args, **kwargs):
        user = request.user
        tour = self.get_object()
        if FavoriteBookingService.remove_favorite(tour=tour, user=user, _type=BookingType.TOUR):
            return Response({"message": "Đã xoá khỏi mục yêu thích!"})
        return Response({"message": "Khôg tồn tại tour này ở mục yêu thích!"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=[HttpMethod.GET])
    def tours_for_coupon(self, request, *args, **kwargs):
        order_by = "-created_at"
        tour_queryset = Tour.objects.filter(owner=request.user).order_by(order_by)
        data = TourCouponSerializer(tour_queryset, many=True).data
        return Response(data)

    @action(detail=True, methods=[HttpMethod.GET])
    def top_tour(self, request, *args, **kwargs):
        queryset = TourService.get_top_tour_recommend_sys()
        serializer = self._list(queryset, request)
        return Response(serializer.data)

    @action(detail=False, methods=[HttpMethod.GET])
    def recommend_for_user(self, request, *args, **kwargs):
        user = request.user
        limit = request.query_params.get("limit", None)
        self.queryset = TourService.recommend_for_user(user, limit)
        return super().list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = TourService.get_filter_query(request)
        serializer = self._list(queryset, request)
        return Response(serializer.data)

    def _list(self, queryset, request):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return serializer

    def create(self, request, *args, **kwargs):
        data, tour_images_link = TourService.init_data_tour(request)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                tour = serializer.save()
                TourImageService.create_tour_image(tour, tour_images_link)
                created_serializer = TourSerializer(tour)
            return Response(created_serializer.data, status=status.HTTP_200_OK)
        return ErrorResponse(ErrorResponseType.CANT_CREATE, params=["tour"])

    def update(self, request, *args, **kwargs):
        tour = self.get_object()
        data, tour_images_link = TourService.init_data_tour(request)
        serializer = self.get_serializer(tour, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            with transaction.atomic():
                TourService.refresh_image(tour)
                self.perform_update(serializer)
                TourImageService.create_tour_image(tour, tour_images_link)
                updated_serializer = TourSerializer(tour)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        return ErrorResponse(ErrorResponseType.CANT_CREATE, params=["tour"])

    @action(detail=False, methods=[HttpMethod.GET])
    def list_tour(self, request, *args, **kwargs):
        user = request.user
        queryset = TourService.list_tour_manage(user)
        serializer = self._list(queryset, request)
        return Response(serializer.data)

    @action(detail=True, methods=[HttpMethod.PUT])
    def deactivate(self, request, *args, **kwargs):
        tour = self.get_object()
        user = request.user
        if TourService.check_deactive_tour(tour, user):
            tour.is_active = False
            tour.save()
            return Response({"message": "Vô hiệu hoá thành công tour!"}, status=status.HTTP_200_OK)
        return Response({"message": "Tour đang được book, không thể vô hiệu hoá"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=[HttpMethod.PUT])
    def activate(self, request, *args, **kwargs):
        tour = self.get_object()
        tour.is_active = True
        tour.save()
        return Response({"message": "Kích hoạt hoá thành công tour!"}, status=status.HTTP_200_OK)

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

    @action(detail=True, methods=[HttpMethod.GET])
    def get_reviews(self, request, *args, **kwargs):
        """
        URL: api/v1/tour/{tour_id}/get_reviews/?page={int}&page_size={int}
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
            "next": "https://bonitravel.online/api/v1/tour/2800076077e74363923b13bfa5acb1f0/get_reviews?page=2"
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
        tour = self.get_object()
        queryset = BookingReviewService.get_tour_review(tour)
        self.queryset = queryset

        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=[HttpMethod.GET])
    def get_available_group_size(self, request, *args, **kwargs):
        tour = self.get_object()
        start_date = request.query_params.get("start_date")
        start_date = Utils.safe_str_to_date(start_date)
        if start_date:
            available_group_size = TourService.get_available_group_size(tour, start_date)
            return Response(dict(available_group_size=available_group_size))
        else:
            return Response(dict(error_message="Invalid start_date field"), status=status.HTTP_400_BAD_REQUEST)
