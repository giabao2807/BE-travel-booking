from django.db import models

from api_general.models import Image
from api_tour.models import Tour
from base.models import BaseSimpleModel


class TourImage(BaseSimpleModel):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="tour_images")
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="tour_images")

    class Meta:
        db_table = 'tour_images'
