from django.db import models

from api_general.models.coupon import Coupon
from api_tour.models import Tour
from base.models import BaseSimpleModel


class TourCoupon(BaseSimpleModel):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="tour_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="tour_coupons")

    class Meta:
        db_table = "tour_coupons"
