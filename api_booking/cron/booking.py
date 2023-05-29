import datetime

from api_booking.models import Booking
from common.constants.api_booking import BookingStatus


def sync_booking_status():
    current_date = datetime.datetime.now()
    last_date = current_date - datetime.timedelta(days=1)
    Booking.objects.filter(status=BookingStatus.UNPAID, updated_at__lt=last_date).update(status=BookingStatus.CANCELED)
    Booking.objects.filter(status=BookingStatus.PAID, end_date__lt=current_date).update(status=BookingStatus.COMPLETED)
