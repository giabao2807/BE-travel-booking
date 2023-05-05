from django.db import models

from api_booking.models import Booking
from base.models import Review


class BookingReview(Review):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)

    class Meta:
        db_table = 'booking_reviews'
