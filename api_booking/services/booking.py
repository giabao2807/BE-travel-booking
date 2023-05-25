from datetime import datetime, timedelta
from typing import List, Dict, Optional

from rest_framework.exceptions import ValidationError

from api_booking.models import Booking, BookingItem
from api_general.services import Utils
from api_general.services.vnpay import VNPayTransaction
from api_hotel.models import Room
from api_hotel.services import HotelService
from api_tour.models import Tour
from api_tour.services import TourService
from base.exceptions import BoniException
from base.exceptions.base import ErrorType


class BookingService:
    @classmethod
    def create(cls, booking_data: dict) -> Booking:
        data_booking_items = booking_data.pop("booking_items", [])
        start_date: datetime = booking_data.get("start_date")
        end_date: datetime = booking_data.get("end_date", None)

        booking_items: List[BookingItem] = []
        booking = Booking(**booking_data)
        booking.save()

        for _booking_item_data in data_booking_items:
            tour_id = _booking_item_data.get("tour_id")
            if tour_id:
                tour = Tour.objects.filter(id=tour_id).first()
                if tour:
                    day_diff = 0
                    total_days = tour.total_days
                    if total_days:
                        day_diff = Utils.safe_int(total_days[0], 1) - 1
                    end_date = start_date + timedelta(days=day_diff)

            booking_items.append(
                BookingItem(
                    booking_id=booking.id,
                    **_booking_item_data
                )
            )

        booking.end_date = end_date
        booking.save()
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
        start_date: datetime = kwargs.get("start_date")
        is_valid: bool = True
        current_tour: Optional[Tour] = Tour.objects.filter(id=tour_id, is_active=True).first()
        if current_tour:
            booked_tour_amount_mapping = TourService.get_booked_tour_amounts(start_date=start_date)
            booked_tour_amount = booked_tour_amount_mapping.get(tour_id, 0)
            if quantity > (current_tour.group_size - booked_tour_amount):
                is_valid = False
                if raise_exception:
                    raise BoniException(ErrorType.GENERAL, ["Số lượng trống của chuyến không đủ"])
        else:
            is_valid = False
            if raise_exception:
                raise BoniException(ErrorType.DEACTIVATED_VN, ["Chuyến"])

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
                    raise BoniException(ErrorType.GENERAL, ["Số lượng phòng trống không còn đủ"])
        else:
            is_valid = False
            if raise_exception:
                raise BoniException(ErrorType.DEACTIVATED_VN, ["Phòng khách sạn"])

        return is_valid

    @classmethod
    def create_payment_link(cls, booking: Booking, bank_code: str, client_ip: str) -> str:
        total_price = cls.get_total_price_from_booking(booking)
        order_info = "Thanh toán hóa đơn trên BoniTravel"
        transaction = VNPayTransaction(total_price, client_ip, bank_code, str(booking.id.hex), order_info)
        transaction.build_payment_url()

        return transaction.url

    @classmethod
    def get_total_price_from_booking(cls, booking: Booking) -> int:
        booking_items: List[BookingItem] = list(booking.booking_item.all())
        total_price = 0

        for booking_item in booking_items:
            item_price = 0
            if booking_item.room:
                current_price = booking_item.room.price
                hotel_id = booking_item.room.hotel_id
                current_coupon = HotelService.get_current_coupon(hotel_id)
            else:
                current_price = booking_item.tour.price
                current_coupon = TourService.get_current_coupon(booking_item.tour_id)

            if current_price:
                item_price = current_price * booking_item.quantity
            if current_coupon:
                item_price = (100 - current_coupon.discount_percent) * item_price

            total_price += item_price

        return round(total_price, -3)
