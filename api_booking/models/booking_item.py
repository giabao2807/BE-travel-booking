from django.db import models

from api_booking.models import Booking
from api_hotel.models import Room
from api_tour.models import Tour
from base.models import BaseSimpleModel


class BookingItem(BaseSimpleModel):
    booking = models.ForeignKey(Booking,
                                on_delete=models.CASCADE, related_name="booking_item")
    tour = models.ForeignKey(Tour, null=True, blank=True,
                             on_delete=models.CASCADE, related_name="booking_item")
    room = models.ForeignKey(Room, null=True, blank=True,
                             on_delete=models.CASCADE, related_name="booking_item")
    quality = models.IntegerField(null=False, default=1)

    class Meta:
        db_table = 'booking_items'
