from django.db import models

from api_hotel.managers import HotelManager
from api_tour.models import City
from api_user.models import Profile
from base.models import TimeStampedModel, Image


class Hotel(TimeStampedModel):
    cover_picture = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    descriptions = models.TextField(null=True, blank=True)
    group_size = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    rules = models.TextField(null=True, blank=True)
    num_review = models.IntegerField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    objects = HotelManager()

    class Meta:
        db_table = 'hotels'


class HotelImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'hotel_image'
