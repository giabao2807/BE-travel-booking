from django.db import models
from django.db.models import Manager

from api_general.consts import CouponType
from api_user.models import Profile
from base.models import TimeStampedModel


class Coupon(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percent = models.PositiveIntegerField()
    for_all = models.BooleanField(default=True)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="coupons")

    objects = Manager

    class Meta:
        db_table = "coupons"
