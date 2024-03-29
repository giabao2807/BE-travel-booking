import os
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

from django.db.models import F, QuerySet, Q, Value, CharField
from django.db.models.functions import Collate, Concat
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError

from api_booking.consts import BookingType
from api_booking.models import Booking, BookingItem
from api_general.models import Coupon
from api_general.services import Utils
from api_general.services.vnpay import VNPayTransaction
from api_hotel.models import Room
from api_hotel.serializers import BookingHotelCardSerializer
from api_hotel.services import HotelService
from api_tour.models import Tour
from api_tour.services import TourService
from api_user.models import Profile
from api_user.statics import RoleData
from base.exceptions import BoniException
from base.exceptions.base import ErrorType
from base.services.send_mail import SendMail
from common.constants.api_booking import BookingStatus
from common.constants.base_const import SupportEnv


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
    def create_payment_link(cls, booking: Booking, bank_code: str, client_ip: str, env: SupportEnv) -> str:
        original_price, coupon_percent = cls.get_original_price_and_coupon_from_booking(booking)
        total_price = original_price * (100 - coupon_percent)
        total_price = round(total_price, -3)
        order_info = "Thanh toán hóa đơn trên BoniTravel"

        transaction = VNPayTransaction(env, total_price, client_ip, bank_code, str(booking.id.hex), order_info)
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
    def send_mail(cls, booking_id: str):
        booking = Booking.objects.filter(id=booking_id).first()
        booking_item = BookingItem.objects.filter(booking=booking).first()
        booking_name = booking_item.tour.name if booking.type == 2 else booking_item.room.hotel.name
        hotel_name = booking_item.room.hotel.address if booking.type == 1 else ""
        total_price = cls.get_total_price(booking.history_origin_price, booking.history_discount_price)
        cls.send_mail_booking_success(booking.customer.email, True, booking.type,
                                      f'{booking.customer.first_name} {booking.customer.last_name}',
                                      booking_name, booking.start_date, booking.end_date,
                                      total_price, os.getenv('BOOKING_LINK'), hotel_name, booking.note)

    @classmethod
    def send_mail_sync_data(cls, cancel_booking, complete_booking, remind_booking):
        admin = Profile.objects.filter(role__id=RoleData.ADMIN.id).first()
        total_cancel = len(cancel_booking) or 0
        total_complete = len(complete_booking) or 0
        total_remind = len(remind_booking) or 0
        cls.send_mail_to_admin_sync(admin.email,
                                    f'{admin.first_name} {admin.last_name}',
                                    total_cancel, total_complete, total_remind)

    @classmethod
    def send_mail_to_admin_sync(cls, email, user_name, total_cancel,
                                total_complete, total_remind):
        content = render_to_string(
            "job_for_admin.html",
            {"total_cancel": total_cancel, "user_name": user_name,
             "total_complete": total_complete, "total_remind": total_remind},
        )
        SendMail.start(
            [email], "[MANAGE SYSTEM] Information about your sync data today!", content
        )

    @classmethod
    def send_mail_booking_success(cls,
                                  email: str, send_mail: bool,
                                  type_booking: int,
                                  user_name: str, booking_name: str,
                                  start_date, end_date,
                                  total_price, link,
                                  hotel_address: str = "",
                                  note: str = "",
                                  ):
        if send_mail:
            link = f"{link}"
            content = render_to_string(
                "booking_success.html",
                {"type_booking": type_booking, "user_name": user_name, "booking_name": booking_name,
                 "hotel_address": hotel_address, "start_date": start_date, "note": note,
                 "end_date": end_date, "total_price": total_price, "link": link},
            )
            SendMail.start(
                [email], "[BOOKING SUCCESS] Information about your booking!", content
            )

    @classmethod
    def send_mail_booking_error(cls, booking: Booking):
        email, type_booking, user_name, booking_name, total_price = cls.get_sum_info_booking(booking)
        content = render_to_string(
            "booking_error.html",
            {"type_booking": type_booking, "user_name": user_name, "booking_name": booking_name,
             "total_price": total_price, "link": os.getenv('BOOKING_LINK')},
        )
        SendMail.start(
            [email], "[BOOKING CANCELED] Information about your booking!", content
        )

    @classmethod
    def send_mail_remind_booking(cls, booking: Booking):
        email, type_booking, user_name, booking_name, total_price = cls.get_sum_info_booking(booking)
        content = render_to_string(
            "remind_booking.html",
            {"type_booking": type_booking, "user_name": user_name, "booking_name": booking_name,
             "total_price": total_price, "link": os.getenv('BOOKING_LINK')},
        )
        SendMail.start(
            [email], "[REMIND BOOKING] Remind for your upcoming travel!", content
        )

    @classmethod
    def get_sum_info_booking(cls, booking: Booking):
        booking_item = BookingItem.objects.filter(booking=booking).first()
        email = booking.customer.email
        type_booking = booking.type
        user_name = f'{booking.customer.last_name} {booking.customer.first_name}'
        booking_name = booking_item.tour.name if booking.type == 2 else booking_item.room.hotel.name
        if booking.history_origin_price and booking.history_discount_price:
            total_price = cls.get_total_price(booking.history_origin_price, booking.history_discount_price)
        else:
            total_price = "Chưa xác định"
        return email, type_booking, user_name, booking_name, total_price


    @classmethod
    def get_total_price(cls, original_price, discount_percent) -> int:
        total_price = original_price * (100 - discount_percent)/100

        return round(total_price, -3)

    @classmethod
    def add_extra_data_hotel(cls, booking_data_list: List[dict]):
        booking_ids = [booking_data.get("id") for booking_data in booking_data_list]
        bookings: List[Booking] = list(
            Booking.objects.filter(id__in=booking_ids).prefetch_related("booking_item__room"))
        hotel_booking_mapping = {
            _booking.id: _booking.booking_item.first().room.hotel_id
            for _booking in bookings
        }

        total_price_mapping = cls.get_bulk_total_prices(booking_data_list, bookings)
        hotel_ids = list(hotel_booking_mapping.values())
        hotel_cards = HotelService.get_hotel_cards(hotel_ids)
        hotel_data_list = BookingHotelCardSerializer(hotel_cards, many=True).data
        for _booking_data in booking_data_list:
            _booking_id = _booking_data.get("id")
            _hotel_id = hotel_booking_mapping.get(_booking_id)
            hotel_data = next(filter(lambda _hotel: _hotel.get("id") == _hotel_id, hotel_data_list))
            booking_instance = next(filter(lambda _booking: _booking.id == _booking_id, bookings))
            _booking_data["hotel"] = hotel_data
            _booking_data["total_price"] = total_price_mapping.get(_booking_id)
            _booking_data["booking_items"] = booking_instance.booking_item.all().values("quantity", "room_id", "room__name").annotate(room_name=F("room__name"))

    @classmethod
    def get_bulk_total_prices(cls, booking_data_list: List[dict], bookings: List[Booking]):
        total_price_mapping = dict()
        empty_price_booking_ids: List[str] = []

        for booking_data in booking_data_list:
            booking_id = booking_data.get("id")
            history_origin_price = booking_data.get("history_origin_price")
            history_discount_price = booking_data.get("history_discount_price")
            if history_origin_price:
                total_price = cls.get_total_price(history_origin_price, history_discount_price)
                total_price_mapping[booking_id] = total_price
            else:
                empty_price_booking_ids.append(booking_id)

        hotel_ids: List[str] = []
        original_price_mapping: Dict[str, dict] = []
        for _empty_price_booking_id in empty_price_booking_ids:
            original_price = 0
            _empty_price_booking = next(filter(lambda _booking: _booking.id == _empty_price_booking_id, bookings))
            hotel_id = _empty_price_booking.booking_item.first().room.hotel_id
            hotel_ids.append(hotel_id)

            for _booking_item in _empty_price_booking.booking_item:
                original_price += (_booking_item.room.price * _booking_item.quantity)
            original_price_mapping[hotel_id] = dict(booking_id=_empty_price_booking_id, original_price=original_price)

        current_discount_percent_mapping = HotelService.get_current_discount_percent_mapping(hotel_ids)
        for hotel_id, discount_percent in current_discount_percent_mapping.items():
            original_price_data = original_price_mapping.get(hotel_id)
            booking_id = original_price_data.get("booking_id")
            original_price = original_price_data.get("original_price")
            total_price_mapping[booking_id] = cls.get_total_price(original_price, discount_percent)

        return total_price_mapping

    @classmethod
    def get_bookings_qs_for_manage(cls, user: Profile, booking_type: BookingType,
                                   name, status: str = None) -> QuerySet:
        booking_ft = Q(type=booking_type)
        if name:
            name = Collate(Value(name.strip()), "utf8mb4_general_ci")

        if user.role.id.hex == RoleData.PARTNER.value.get('id'):
            if booking_type == BookingType.TOUR:
                booking_ft &= Q(booking_item__tour__owner=user)
            else:
                booking_ft &= Q(booking_item__room__hotel__owner=user)

        if booking_type == BookingType.TOUR:
            booking_ft &= Q(booking_item__tour__name__icontains=name)
        else:
            booking_ft &= Q(booking_item__room__hotel__name__icontains=name)

        if status:
            booking_ft &= Q(status=status)

        unique_booking_ids = Booking.objects.filter(booking_ft).values_list("id", flat=True).distinct()
        booking_qs = Booking.objects.filter(id__in=unique_booking_ids).order_by("-created_at")

        return booking_qs
