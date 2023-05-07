from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_hotel.models import Hotel


class HotelSerializer(ModelSerializer):

    class Meta:
        model = Hotel
        fields = "__all__"


class HotelCardSerializer(ModelSerializer):
    price_range = serializers.SerializerMethodField()
    rate_average = serializers.FloatField(read_only=True)

    def get_price_range(self, instance):
        price_range = ""
        min_price = instance.get("min_price")
        max_price = instance.get("max_price")

        if min_price and max_price:
            price_range = "{:,}".format(min_price) + " - " + "{:,}".format(max_price)

        return price_range

    class Meta:
        model = Hotel
        fields = ("name", "address", "price_range", "cover_picture", "rate_average")
