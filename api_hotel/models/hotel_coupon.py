from django.db import models

from api_general.models.coupon import Coupon
from api_hotel.models import Hotel
from base.models import BaseSimpleModel


class HotelCoupon(BaseSimpleModel):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="hotel_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="hotel_coupons")

    class Meta:
        db_table = "hotel_coupons"
