from datetime import datetime
from typing import List, Dict, Optional

from rest_framework.exceptions import ValidationError

from api_booking.models import Booking, BookingItem
from api_hotel.models import Room
from api_hotel.services import HotelService
from api_tour.models import Tour


class BookingService:
    @classmethod
    def create(cls, booking_data: dict) -> Booking:
        data_booking_items = booking_data.pop("booking_items", [])
        booking_items: List[BookingItem] = []
        booking = Booking(**booking_data)
        booking.save()

        for _booking_item_data in data_booking_items:
            booking_items.append(
                BookingItem(
                    booking_id=booking.id,
                    **_booking_item_data
                )
            )

        BookingItem.objects.bulk_create(booking_items)

        return booking

    @classmethod
    def create_payment_order(cls, booking: Booking):
        pass

    @classmethod
    def validate_tour_booking(cls, tour_id, quantity: int, **kwargs) -> bool:
        """

        @param tour_id:
        @param quantity:
        @param kwargs:
        Accept:
        - raise_exception: (bool) Set it to True if you want to raise a ValidationError immediately
        @return:
        """
        raise_exception: bool = kwargs.get("raise_exception", False)
        is_valid: bool = True
        current_tour: Optional[Tour] = Tour.objects.filter(id=tour_id, is_active=True).first()
        if current_tour:
            if quantity > current_tour.group_size:
                is_valid = False
                if raise_exception:
                    raise ValidationError("The quantity for this tour is not available for now")
        else:
            is_valid = False
            if raise_exception:
                raise ValidationError("This tour is not available!")

        return is_valid

    @classmethod
    def validate_room_booking(cls, room_id, quantity: int, start_date: datetime, end_date: datetime, **kwargs) -> bool:
        """

        @param room_id:
        @param quantity:
        @param start_date:
        @param end_date:
        @param kwargs:
        @return:
        """
        is_valid: bool = True
        raise_exception: bool = kwargs.get("raise_exception", False)
        booked_room_amount: Dict[str, int] = HotelService.get_booked_rooms_in_range(start_date, end_date, room_id=room_id)
        booked_amount = booked_room_amount.get(room_id, 0)
        current_room = Room.objects.filter(id=room_id, is_active=True).first()
        if current_room:
            if quantity > current_room.quantity - booked_amount:
                is_valid = False
                if raise_exception:
                    raise ValidationError("The quantity for this room is not available for now")
        else:
            is_valid = False
            if raise_exception:
                raise ValidationError("This room is not available!")

        return is_valid
