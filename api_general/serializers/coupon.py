import datetime

from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.serializers import ModelSerializer

from api_general.models import Coupon
from api_general.services.coupon import CouponService


class CouponSerializer(ModelSerializer):

    class Meta:
        model = Coupon
        fields = "__all__"

    def validate(self, attrs: dict):
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        if start_date > end_date:
            raise ValidationError("start date must be less than or equal end date")

        return attrs


class SimpleCouponSerializer(ModelSerializer):

    class Meta:
        model = Coupon
        fields = ("id", "name", "start_date", "end_date", "discount_percent")


class CUCouponSerializer(ModelSerializer):
    partner_ids = serializers.ListField(child=serializers.UUIDField(), allow_null=True, required=False, read_only=True)

    class Meta:
        model = Coupon
        fields = "__all__"

    def validate_start_date(self, start_date):
        if start_date.date() < datetime.datetime.now().date():
            raise ValidationError("start_date must greater than current date")

        return start_date

    def validate(self, attrs):
        for_all = attrs.get("for_all", False)
        partner_ids = self.initial_data.get("partner_ids", [])
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        if not for_all and not partner_ids:
            raise ValidationError("Partner ids or for_all must has value")
        if start_date > end_date:
            raise ValidationError("start date must be less than or equal end date")

        return attrs

    def save(self, **kwargs):
        partner_ids = self.initial_data.pop("partner_ids", [])

        coupon = super().save(**kwargs)
        if self.instance:
            coupon.hotel_coupons.all().delete()
            coupon.tour_coupons.all().delete()
        if partner_ids:
            CouponService.refresh_hotel_tour_coupons(coupon, partner_ids)

        return coupon
