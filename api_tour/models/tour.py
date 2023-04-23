from django.db import models
from base.models import TimeStampedModel


class Tour(TimeStampedModel):
    name = models.CharField(max_length=255)
    total_days = models.FloatField(null=True, blank=True)
    descriptions = models.TextField(null=True, blank=True)
    group_size = models.IntegerField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    rate = models.FloatField(null=True, blank=True)
    schedule_content = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
