from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_hotel.models import Hotel
from api_hotel.services import HotelService


class HotelSerializer(ModelSerializer):
    coupon_data = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        exclude = ['is_active']

    def get_coupon_data(self, instance):
        from api_hotel.services import HotelService
        from api_general.serializers import SimpleCouponSerializer

        coupon = HotelService.get_current_coupon(instance.id)
        coupon_data = dict()
        if coupon:
            coupon_data = SimpleCouponSerializer(coupon).data

        return coupon_data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['num_review'] = HotelService.count_num_review(instance)
        ret['list_images'] = [i.image.link for i in instance.hotel_images.all()]
        return ret


class CUHotelSerializer(ModelSerializer):
    hotel_images = serializers.ListField(child=serializers.FileField(), required=True, write_only=True)

    class Meta:
        model = Hotel
        fields = [
            "id", "cover_picture", "name", "address",
            "descriptions", "rules", "city", "owner", "longitude", "latitude", "hotel_images"
        ]

    @transaction.atomic
    def create(self, validated_data):
        hotel_images = validated_data.pop("hotel_images")
        hotel = super().create(validated_data)
        HotelService.bulk_create_hotel_images(hotel_images, hotel.id)
        return hotel


class HotelCardSerializer(ModelSerializer):
    num_review = serializers.IntegerField()
    rate_average = serializers.FloatField(read_only=True)
    coupon_data = serializers.SerializerMethodField()
    min_price = serializers.IntegerField()
    max_price = serializers.IntegerField()

    def get_coupon_data(self, instance):
        from api_hotel.services import HotelService
        from api_general.serializers import SimpleCouponSerializer

        coupon = HotelService.get_current_coupon(instance.get("id"))
        coupon_data = dict()
        if coupon:
            coupon_data = SimpleCouponSerializer(coupon).data

        return coupon_data

    class Meta:
        model = Hotel
        fields = ("id", "name", "address", "num_review",
                  "min_price", "max_price",
                  "cover_picture", "rate_average", "coupon_data")


class BookingHotelCardSerializer(ModelSerializer):
    num_review = serializers.IntegerField()
    rate_average = serializers.FloatField(read_only=True)
    min_price = serializers.IntegerField()
    max_price = serializers.IntegerField()

    class Meta:
        model = Hotel
        fields = ("id", "name", "address", "num_review",
                  "min_price", "max_price", "cover_picture", "rate_average")
