from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from api_booking.models import FavoriteBooking
from api_hotel.serializers import BookingHotelCardSerializer
from api_hotel.services import HotelService
from api_tour.serializers import CardTourSerializer


class ListHotelFavoriteSerializer(ModelSerializer):

    class Meta:
        model = FavoriteBooking
        fields = "__all__"

    def to_representation(self, instance: FavoriteBooking):
        data = super().to_representation(instance)
        hotel = HotelService.get_hotel_cards(instance.hotel.id)
        if hotel:
            hotel = hotel.first()
            data["hotel"] = BookingHotelCardSerializer(hotel).data

        return data


class ListTourFavoriteSerializer(ModelSerializer):

    class Meta:
        model = FavoriteBooking
        fields = "__all__"

    def to_representation(self, instance: FavoriteBooking):
        data = super().to_representation(instance)
        tour = instance.tour
        data["tour"] = CardTourSerializer(tour).data
        return data
