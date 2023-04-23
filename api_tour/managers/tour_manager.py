from django.db import models


class TourManager(models.Manager):
    def by_city(self, city: str):
        return self.get_queryset().filter(city=city)
