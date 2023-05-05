from django.db import models

from api_general.models import Image
from api_hotel.models import RoomType


class RoomTypeImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='room_type_images')

    class Meta:
        db_table = 'room_type_images'
