from django.db import models

from api_user.models import Profile
from base.models import TimeStampedModel


class Review(TimeStampedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    rate = models.FloatField()
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        abstract = True
