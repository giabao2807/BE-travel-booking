from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_general.serializers import SimpleCouponSerializer
from api_tour.models import Tour
from api_tour.models.tour_image import TourImage
from api_tour.services import TourService
from api_user.statics import RoleData


class TourCouponSerializer(ModelSerializer):
    class Meta:
        model = Tour
        fields = ('id', 'name')


class CreateTourSerializer(ModelSerializer):
    class Meta:
        model = Tour
        exclude = ('rate', 'longitude', 'latitude')


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
        ret['num_review'] = TourService.count_num_review(instance)
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
                  'rate', 'city', 'departure', 'traffics', "coupon_data",
                  "is_active")

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
        ret['num_review'] = TourService.count_num_review(instance)
        ret['rate'] = 4.5
        return ret


class CardFavoriteTourSerializer(ModelSerializer):
    coupon_data = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ('id', 'name', 'cover_picture', 'group_size',
                  'total_days', 'language_tour', 'price',
                  'rate', 'city', 'departure', 'traffics', "coupon_data",
                  "is_active")

    def get_coupon_data(self, instance):
        _id = instance.id if isinstance(instance, Tour) else instance.get("id")
        coupon = TourService.get_current_coupon(_id)
        coupon_data = dict()
        if coupon:
            coupon_data = SimpleCouponSerializer(coupon).data

        return coupon_data

    def to_representation(self, instance):
        from api_booking.models import FavoriteBooking
        ret = super().to_representation(instance)
        ret['city'] = instance.city.name if instance.city else 'Việt Nam'
        ret['num_review'] = TourService.count_num_review(instance)
        ret['rate'] = 4.5
        user = self.context["request"].user

        if not user.is_anonymous and user.role.id.hex == RoleData.ADMIN.id:
            return ret
        ret['is_favorite'] = False
        if not user.is_anonymous:
            favorite = FavoriteBooking.objects.filter(customer=user, tour=instance).first()
            ret['is_favorite'] = True if favorite else False
        return ret
