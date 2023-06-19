from django.db.models import Manager
from django.utils import timezone

from django.db import models

from api_booking.consts import BookingType
from api_general.consts import BankCodes
from api_hotel.models import Hotel
from api_tour.models import Tour
from api_user.models import Profile
from base.models import TimeStampedModel


class FavoriteBooking(TimeStampedModel):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='favorite_booking')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True)
    type = models.IntegerField(choices=BookingType.choices, default=BookingType.HOTEL)

    objects = Manager

    class Meta:
        db_table = 'booking_favorites'
