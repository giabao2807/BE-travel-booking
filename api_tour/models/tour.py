from django.db import models

from api_tour.managers import TourManager
from api_tour.models import City
from api_user.models import Profile
from base.models import TimeStampedModel, Image


class Tour(TimeStampedModel):
    cover_picture = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    total_days = models.CharField(max_length=30, null=True, blank=True)
    language_tour = models.CharField(max_length=255, null=True, blank=True)
    descriptions = models.TextField(null=True, blank=True)
    group_size = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    schedule_content = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    num_review = models.IntegerField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)

    objects = TourManager()

    class Meta:
        db_table = 'tours'


class TourImage(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'tour_image'
