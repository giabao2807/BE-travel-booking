from django.db import models

from base.models import BaseSimpleModel


class City(BaseSimpleModel):
    name = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'cities'
