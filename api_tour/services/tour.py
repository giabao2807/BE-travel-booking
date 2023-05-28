from datetime import datetime

from django.db.models import Q, QuerySet, Sum

from api_booking.consts import BookingType
from api_general.models import Coupon
from api_general.services import Utils
from api_tour.models import Tour
from common.constants.api_booking import BookingStatus


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

    @classmethod
    def get_booked_tour_amounts(cls, start_date: datetime, tour_id: str = ""):
        valid_booking_status = [BookingStatus.PAID, BookingStatus.UNPAID]
        tour_ft = Q(booking_item__booking__start_date__date=start_date.date()) & \
                     Q(booking_item__booking__type=BookingType.TOUR) & \
                     Q(booking_item__booking__status__in=valid_booking_status) & \
                     Q(is_active=True)

        if tour_id:
            tour_ft &= Q(id=tour_id)
        booked_tour_mapping = dict(
            Tour.objects.filter(tour_ft).values("id")
                .annotate(booked_tour_amount=Sum("booking_item__quantity"))
                .values_list("id", "booked_tour_amount")
        )

        return booked_tour_mapping

    @classmethod
    def get_available_group_size(cls, tour: Tour, start_date: datetime) -> int:
        booked_amount_mapping = cls.get_booked_tour_amounts(start_date, tour.id)
        booked_amount = booked_amount_mapping.get(tour.id, 0)

        return tour.group_size - booked_amount
