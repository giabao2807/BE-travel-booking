from datetime import datetime

from django.db.models import Q, QuerySet

from api_general.models import Coupon
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

    @classmethod
    def get_current_coupon(cls, tour_id: str) -> Coupon:
        current_date = datetime.now().date()
        base_ft = Q(
            is_active=True,
            start_date__date__lte=current_date,
            end_date__date__gte=current_date
        )

        for_all_coupon_ft = Q(for_all=True)
        selected_tours_coupon_ft = Q(for_all=False, tour_coupons__tour_id=tour_id)
        tour_coupon_ft = base_ft & (for_all_coupon_ft | selected_tours_coupon_ft)
        coupon = Coupon.objects.filter(tour_coupon_ft).order_by("-discount_percent").first()

        return coupon
