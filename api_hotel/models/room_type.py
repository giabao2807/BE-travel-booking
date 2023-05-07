from django.db import models

from api_hotel.models import Hotel
from base.models import TimeStampedModel


class RoomType(TimeStampedModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    beds = models.CharField(max_length=255, null=True, blank=True)
    adults = models.IntegerField(null=True, blank=True)
    children = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    price = models.IntegerField(null=False, blank=False)
    square = models.CharField(max_length=255, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')

    class Meta:
        db_table = 'room_types'
