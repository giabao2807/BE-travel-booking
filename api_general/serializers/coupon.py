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
    hotel_ids = serializers.ListField(allow_null=True, required=False, read_only=True)
    tour_ids = serializers.ListField(allow_null=True, required=False, read_only=True)

    class Meta:
        model = Coupon
        fields = "__all__"

    def validate_start_date(self, start_date):
        if start_date.date() < datetime.datetime.now().date():
            raise ValidationError("start_date must greater than current date")

        return start_date

    def validate(self, attrs):
        for_all = attrs.get("for_all", False)
        hotel_ids = self.initial_data.get("hotel_ids", [])
        tour_ids = self.initial_data.get("tour_ids", [])
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        if not for_all and not any([hotel_ids, tour_ids]):
            raise ValidationError("Hotel ids or tour ids must not be null in the same time in case for_all is false")
        if start_date > end_date:
            raise ValidationError("start date must be less than or equal end date")

        return attrs

    def create(self, validated_data):
        hotel_ids = self.initial_data.get("hotel_ids", [])
        tour_ids = self.initial_data.get("tour_ids", [])
        coupon = CouponService.create(validated_data, hotel_ids, tour_ids)

        return coupon

    def update(self, instance, validated_data):
        hotel_ids = self.initial_data.get("hotel_ids", [])
        tour_ids = self.initial_data.get("tour_ids", [])
        coupon_data = dict(hotel_ids=hotel_ids, tour_ids=tour_ids)

        instance = super().update(instance, validated_data)
        CouponService.update_related(instance, coupon_data)

        return instance
