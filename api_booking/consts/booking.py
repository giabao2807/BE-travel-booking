from django.db.models import IntegerChoices


class BookingType(IntegerChoices):
    HOTEL = 1
    TOUR = 2
