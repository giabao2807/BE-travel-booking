from datetime import datetime, timedelta
from typing import List, Dict, Optional

from rest_framework.exceptions import ValidationError

from api_booking.consts import BookingType
from api_booking.models import Booking, BookingItem
from api_general.models import Coupon
from api_general.services import Utils
from api_general.services.vnpay import VNPayTransaction
from api_hotel.models import Room
from api_hotel.services import HotelService
from api_tour.models import Tour
from api_tour.services import TourService
from base.exceptions import BoniException
from base.exceptions.base import ErrorType
from common.constants.api_booking import BookingStatus


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
        original_price, coupon_percent = cls.get_original_price_and_coupon_from_booking(booking)
        total_price = original_price * (100 - coupon_percent)
        total_price = round(total_price, -3)
        order_info = "Thanh toán hóa đơn trên BoniTravel"

        transaction = VNPayTransaction(total_price, client_ip, bank_code, str(booking.id.hex), order_info)
        transaction.build_payment_url()

        return transaction.url

    @classmethod
    def get_total_price_by_booking(cls, booking: Booking) -> int:
        total_price = 0
        booking_type = booking.type
        history_origin_price = booking.history_origin_price
        history_discount_price = booking.history_discount_price

        related_fields = ["room"] if booking_type == BookingType.HOTEL else ["tour"]
        if not history_origin_price:
            history_origin_price, history_discount_price = BookingService.get_original_price_and_coupon_from_booking(
                booking, related_fields=related_fields
            )

        if history_origin_price:
            total_price = BookingService.get_total_price(history_origin_price, history_discount_price)
        return total_price

    @classmethod
    def get_original_price_and_coupon_from_booking(cls, booking: Booking, **kwargs) -> (int, int):
        select_related_fields = kwargs.get("related_fields", ["room", "tour"])

        original_price = 0
        booking_type = booking.type
        booking_items: List[BookingItem] = list(booking.booking_item.all().select_related(*select_related_fields))
        current_coupon: Optional[Coupon] = cls.get_current_coupon_by_type(booking_type, booking_items)
        coupon_percent = current_coupon.discount_percent if current_coupon else 0

        for booking_item in booking_items:
            current_price = booking_item.room.price if booking_type == BookingType.HOTEL else booking_item.tour.price
            original_price += (current_price * booking_item.quantity)

        return original_price, coupon_percent

    @classmethod
    def get_current_coupon_by_type(cls, booking_type, booking_items: List[BookingItem]) -> Optional[Coupon]:
        if booking_type == BookingType.HOTEL:
            hotel_id = booking_items[0].room.hotel_id
            current_coupon: Optional[Coupon] = HotelService.get_current_coupon(hotel_id)
        else:
            tour_id = booking_items[0].tour_id
            current_coupon: Optional[Coupon] = TourService.get_current_coupon(tour_id)

        return current_coupon

    @classmethod
    def set_paid_booking(cls, booking_id: str):
        booking = Booking.objects.filter(id=booking_id).first()
        original_price, coupon_percent = cls.get_original_price_and_coupon_from_booking(booking)
        booking.history_origin_price = original_price
        booking.history_discount_price = coupon_percent
        booking.status = BookingStatus.PAID
        booking.save()

    @classmethod
    def get_total_price(cls, original_price, discount_percent) -> int:
        total_price = original_price * (100 - discount_percent)

        return round(total_price, -3)
