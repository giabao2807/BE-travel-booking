from django.db import models

from api_general.models import City, Image
from api_hotel.managers import HotelManager
from api_user.models import Profile
from base.models import TimeStampedModel


class Hotel(TimeStampedModel):
    cover_picture = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    descriptions = models.TextField(null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    rules = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    objects = HotelManager()

    class Meta:
        db_table = 'hotels'
