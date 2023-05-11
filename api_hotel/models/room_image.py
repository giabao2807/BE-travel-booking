from django.db import models

from api_general.models import Image
from api_hotel.models import Room


class RoomImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_images')

    class Meta:
        db_table = 'room_images'
