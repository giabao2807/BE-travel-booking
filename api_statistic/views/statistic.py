from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api_statistic.services import StatisticService
from api_statistic.services.view import StatisticViewService
from api_tour.models import Tour
from api_tour.serializers import TourSerializer, CardTourSerializer
from api_tour.services import TourService
from api_user.permission import PartnerPermission
from base.views import BaseViewSet
from common.constants.base import HttpMethod, ErrorResponse, ErrorResponseType


class StatisticViewSet(BaseViewSet):
    permission_classes = [PartnerPermission]

    permission_map = {
        "revenue_by_date": [PartnerPermission],
        "revenue_by_date": [PartnerPermission],
    }

    @action(detail=False, methods=[HttpMethod.GET])
    def revenue_by_date(self, request, *args, **kwargs):
        user = request.user
        request_params = request.query_params.dict()
        start_date = request_params.get("start_date", "")
        end_date = request_params.get("end_date", "")

        if start_date or end_date:
            start_date, end_date = StatisticViewService.validate_filter_by_date_params(start_date, end_date)
            statistics = StatisticService.get_revenue_statistic(user, start_date, end_date)
        else:
            statistics = StatisticService.get_revenue_statistic(user)

        return Response(statistics, status=status.HTTP_200_OK)

    @action(detail=False, methods=[HttpMethod.GET])
    def box_dashboard(self, request, *args, **kwargs):
        user = request.user
        res = StatisticService.get_box_dashboard(user)
        return Response(res, status=status.HTTP_200_OK)
