from django.db import models

from api_general.models import City
from api_tour.managers import TourManager
from api_user.models import Profile
from base.models import TimeStampedModel


class Tour(TimeStampedModel):
    cover_picture = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    total_days = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    language_tour = models.CharField(default="Việt Nam", max_length=255, null=True, blank=True)
    descriptions = models.TextField(null=True, blank=True)
    group_size = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    schedule_content = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    departure = models.CharField(max_length=255, null=True, blank=True)
    traffics = models.CharField(max_length=255, null=True, blank=True)

    objects = TourManager()

    class Meta:
        db_table = 'tours'
