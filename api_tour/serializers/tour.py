from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_general.serializers import SimpleCouponSerializer
from api_tour.models import Tour
from api_tour.models.tour_image import TourImage
from api_tour.services import TourService


class TourSerializer(ModelSerializer):
    coupon_data = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = "__all__"

    def get_coupon_data(self, instance):
        _id = instance.id if isinstance(instance, Tour) else instance.get("id")
        coupon = TourService.get_current_coupon(_id)
        coupon_data = dict()
        if coupon:
            coupon_data = SimpleCouponSerializer(coupon).data

        return coupon_data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['city'] = instance.city.name if instance.city else 'Việt Nam'
        ret['rate'] = 4.5
        tour_image = TourImage.objects.filter(tour=instance)
        ret['list_images'] = [image.image.link for image in tour_image]
        return ret


class CardTourSerializer(ModelSerializer):
    coupon_data = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ('id', 'name', 'cover_picture', 'group_size',
                  'total_days', 'language_tour', 'price',
                  'rate', 'num_review', 'city', 'departure', 'traffics', "coupon_data")

    def get_coupon_data(self, instance):
        _id = instance.id if isinstance(instance, Tour) else instance.get("id")
        coupon = TourService.get_current_coupon(_id)
        coupon_data = dict()
        if coupon:
            coupon_data = SimpleCouponSerializer(coupon).data

        return coupon_data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['city'] = instance.city.name if instance.city else 'Việt Nam'
        ret['rate'] = 4.5
        return ret
