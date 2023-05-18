from datetime import datetime

from django.db.models import Q, QuerySet

from api_general.services import Utils
from api_tour.models import Tour


class TourService:
    @classmethod
    def filter_by_date(cls, start_date: datetime, end_date: datetime) -> QuerySet:
        diff_dates = (end_date - start_date).days + 1
        tour_ft = Q(is_active=True) & Q(total_days__lt=f"{diff_dates + 1} ngày")
        tour_qs = Tour.objects.filter(tour_ft).order_by("-total_days")

        print(Utils.get_raw_query(tour_qs))

        return tour_qs
