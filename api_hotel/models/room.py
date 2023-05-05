from django.db import models

from api_hotel.models import RoomType
from base.models import TimeStampedModel
from common.constants.api_hotel.room import RoomStatus


class Room(TimeStampedModel):
    status = models.CharField(max_length=255, default=RoomStatus.AVAILABLE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')

    class Meta:
        db_table = 'rooms'
