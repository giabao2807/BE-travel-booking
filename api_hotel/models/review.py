from django.db import models

from api_hotel.models import Hotel
from base.models import Review


class HotelReview(Review):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'hotel_reviews'
