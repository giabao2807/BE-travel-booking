import datetime

from api_booking.models import Booking
from api_booking.services import BookingService
from common.constants.api_booking import BookingStatus


def sync_booking_status():
    current_date = datetime.datetime.now()
    last_date = current_date - datetime.timedelta(days=1)
    start_date_need_remind = current_date + datetime.timedelta(days=1)
    # cancel booking
    canceled_booking = Booking.objects.filter(status=BookingStatus.UNPAID, updated_at__lt=last_date)
    for booking in canceled_booking:
        booking.status = BookingStatus.CANCELED
        BookingService.send_mail_booking_error(booking)
    # remind bookinng
    remind_bookings = Booking.objects.filter(status=BookingStatus.PAID, start_date=start_date_need_remind)
    for booking in remind_bookings:
        BookingService.send_mail_remind_booking(booking)
    # complete booking
    Booking.objects.filter(status=BookingStatus.PAID, end_date__lt=current_date).update(status=BookingStatus.COMPLETED)
