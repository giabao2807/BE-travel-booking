from django.utils import timezone

from django.db import models

from api_user.models import Profile
from base.models import TimeStampedModel
from common.constants.api_booking import BookingStatus


class Booking(TimeStampedModel):
    status = models.CharField(max_length=255, default=BookingStatus.UNPAID, null=True, blank=True)
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    start_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    end_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'bookings'
