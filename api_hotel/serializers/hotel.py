from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_hotel.models import Hotel


class HotelSerializer(ModelSerializer):

    class Meta:
        model = Hotel
        exclude = ['is_active']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['num_review'] = instance.hotel_reviews.count()
        ret['list_images'] = [i.image.link for i in instance.hotel_images.all()]
        return ret


class HotelCardSerializer(ModelSerializer):
    price_range = serializers.SerializerMethodField()
    num_review = serializers.IntegerField()
    rate_average = serializers.FloatField(read_only=True)

    def get_price_range(self, instance):
        price_range = ""
        min_price = instance.get("min_price")
        max_price = instance.get("max_price")

        if min_price and max_price:
            price_range = "{:,}".format(min_price) + " - " + "{:,}".format(max_price) + " VNĐ"

        return price_range

    class Meta:
        model = Hotel
        fields = ("id", "name", "address", "num_review",
                  "price_range", "cover_picture", "rate_average")
