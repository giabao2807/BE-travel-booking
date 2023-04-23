from django.db import models

from base.models import Image, BaseSimpleModel


class City(BaseSimpleModel):
    name = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'cities'


class CityImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, unique=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'city_image'
