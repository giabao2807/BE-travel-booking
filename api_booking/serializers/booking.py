from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from api_booking.consts import BookingType
from api_booking.models import Booking, BookingItem
from api_booking.serializers import CUBookingItemSerializer
from api_booking.services.booking import BookingService
from api_hotel.serializers import BookingHotelCardSerializer
from api_hotel.services import HotelService
from api_tour.serializers import CardTourSerializer


class BookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = "__all__"


class ListBookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = ("id", "start_date", "end_date", "note", "history_origin_price", "history_discount_price", "status")

    def to_representation(self, instance: Booking):
        data = super(ListBookingSerializer, self).to_representation(instance)
        data["total_price"] = BookingService.get_total_price_by_booking(instance)

        booking_type = instance.type
        if booking_type == BookingType.HOTEL:
            hotel_id = instance.booking_item.all().first().room.hotel_id
            hotel = HotelService.get_hotel_cards([hotel_id])
            if hotel:
                hotel = hotel.first()
                data["hotel"] = BookingHotelCardSerializer(hotel).data
            booking_items = list(instance.booking_item.all().values("quantity", "room_id", "room__name").annotate(room_name=F("room__name")))
        else:
            booking_item = instance.booking_item.all().first()
            if booking_item:
                tour = booking_item.tour
                data["tour"] = CardTourSerializer(tour).data
            booking_items = list(instance.booking_item.all().values("quantity"))

        data["booking_items"] = booking_items

        return data


class ListHotelBookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = ("id", "start_date", "end_date", "note", "history_origin_price", "history_discount_price", "status")

    def to_representation(self, instance: Booking):
        data = super(ListHotelBookingSerializer, self).to_representation(instance)
        data["total_price"] = BookingService.get_total_price_by_booking(instance)

        booking_items = list(
            instance.booking_item.all()
                .values("quantity", "room_id")
                .annotate(room_name=F("room__name"), hotel_id=F("room__hotel_id"))
        )
        hotel_id = booking_items[0].get("hotel_id")
        hotel = HotelService.get_hotel_cards(hotel_id)
        if hotel:
            hotel = hotel.first()
            data["hotel"] = BookingHotelCardSerializer(hotel).data

        data["booking_items"] = booking_items

        return data


class ListTourBookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = ("id", "start_date", "end_date", "note", "history_origin_price", "history_discount_price", "status")

    def to_representation(self, instance: Booking):
        data = super(ListTourBookingSerializer, self).to_representation(instance)
        data["total_price"] = BookingService.get_total_price_by_booking(instance)

        booking_item: BookingItem = instance.booking_item.all().select_related("tour").first()
        if booking_item:
            tour = booking_item.tour
            data["tour"] = CardTourSerializer(tour).data
            data["booking_items"] = dict(quantity=booking_item.quantity)

        return data


class CUBookingSerializer(ModelSerializer):
    booking_items = CUBookingItemSerializer(required=True, many=True)
    start_date = serializers.DateTimeField(required=True)
    end_date = serializers.DateTimeField(required=False, allow_null=True)
    type = serializers.IntegerField(required=True)

    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        if end_date and start_date > end_date:
            raise ValidationError("start_date must not greater than end_date")

        return attrs

    def validate_booking_items(self, booking_items):
        if not booking_items:
            raise ValidationError("booking_items field must has value")

        return booking_items

    def create(self, validated_data):
        booking: Booking = BookingService.create(validated_data)

        return booking

    def validate(self, attrs):
        booking_items = attrs.get("booking_items", [])
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        for _booking_item in booking_items:
            room_id = _booking_item.get("room_id", "")
            tour_id = _booking_item.get("tour_id", "")
            quantity = _booking_item.get("quantity", 0)

            if room_id:
                BookingService.validate_room_booking(room_id, quantity, start_date, end_date, raise_exception=True)
            if tour_id:
                BookingService.validate_tour_booking(tour_id, quantity, start_date=start_date, raise_exception=True)

        return attrs
