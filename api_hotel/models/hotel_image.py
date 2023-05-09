from django.db import models
from django.db.models import Manager

from api_general.models import Image
from api_hotel.models import Hotel


class HotelImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="hotel_images")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="hotel_images")

    objects = Manager

    class Meta:
        db_table = 'hotel_images'
