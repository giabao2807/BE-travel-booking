from rest_framework.serializers import ModelSerializer

from api_booking.models import FavoriteBooking
from api_hotel.serializers import BookingHotelCardSerializer
from api_hotel.services import HotelService
from api_tour.serializers.tour import CardTourSerializer


class ListHotelFavoriteSerializer(ModelSerializer):

    class Meta:
        model = FavoriteBooking
        fields = ('id', 'type', "created_at")

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
        fields = ('id', 'type', "created_at")

    def to_representation(self, instance: FavoriteBooking):
        data = super().to_representation(instance)
        tour = instance.tour
        data["tour"] = CardTourSerializer(tour).data
        return data
