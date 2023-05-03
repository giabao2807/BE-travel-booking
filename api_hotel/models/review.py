from django.db import models

from api_hotel.models import Hotel
from api_tour.managers import TourManager
from api_user.models import Profile
from base.models import TimeStampedModel


class Review(TimeStampedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=255)
    rate = models.FloatField(null=True, blank=True)
    hotel_id = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)

    objects = TourManager()

    class Meta:
        db_table = 'reviews'
