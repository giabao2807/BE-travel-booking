import datetime

from api_booking.models import Booking
from api_booking.services import BookingService
from common.constants.api_booking import BookingStatus


def sync_booking_status():
    current_date = datetime.datetime.now()
    last_date = current_date - datetime.timedelta(days=1)
    start_date_need_remind = current_date + datetime.timedelta(days=1)
    # cancel booking
    canceled_booking = Booking.objects.filter(status=BookingStatus.UNPAID,
                                              updated_at__lt=datetime.datetime.combine(last_date, datetime.time.max))
    for booking in canceled_booking:
        booking.status = BookingStatus.CANCELED
        BookingService.send_mail_booking_error(booking)
        booking.save()
    # remind bookinng
    remind_bookings = Booking.objects.filter(status=BookingStatus.PAID,
                                             start_date__range=(datetime.datetime.combine(start_date_need_remind,
                                                                                          datetime.time.min),
                                                                datetime.datetime.combine(start_date_need_remind,
                                                                                          datetime.time.max)))
    for booking in remind_bookings:
        BookingService.send_mail_remind_booking(booking)
    # complete booking
    completed_booking = Booking.objects.filter(status=BookingStatus.PAID,
                                               end_date__lt=datetime.datetime.combine(current_date, datetime.time.max))
    for booking in completed_booking:
        booking.status = BookingStatus.COMPLETED
        booking.save()

    # sync_data
    from api_general.services import RecommendService
    RecommendService.sync_data()

    # info to admin
    BookingService.send_mail_sync_data(canceled_booking, completed_booking, remind_bookings)
