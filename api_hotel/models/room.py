from django.db import models

from api_hotel.models import Hotel
from base.models import TimeStampedModel


class Room(TimeStampedModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    beds = models.CharField(max_length=255, null=True, blank=True)
    adults = models.IntegerField(null=True, blank=True)
    children = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=False)
    square = models.CharField(max_length=255, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, null=True, on_delete=models.CASCADE, related_name='rooms')
    quantity = models.IntegerField(default=1, null=False, blank=False)
    benefit = models.CharField(max_length=1028, null=True, blank=True)

    class Meta:
        db_table = 'rooms'
