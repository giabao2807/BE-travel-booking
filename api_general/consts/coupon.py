from django.db.models import IntegerChoices


class CouponType(IntegerChoices):
    HOTEL = 1
    TOUR = 2
