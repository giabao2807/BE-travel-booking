from django.db import models
from django.db.models import Manager

from api_general.models import Image, City


class CityImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="city_images")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="city_images")

    objects = Manager

    class Meta:
        db_table = 'city_images'
