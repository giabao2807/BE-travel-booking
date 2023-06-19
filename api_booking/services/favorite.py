from api_booking.consts import BookingType
from api_booking.models import FavoriteBooking


class FavoriteBookingService:
    @classmethod
    def add_favorite(cls, user, _type=BookingType.HOTEL, hotel=None, tour=None):
        fav_obj = FavoriteBooking.objects.filter(customer=user, hotel=hotel, tour=tour).first()
        if fav_obj:
            return False
        fav_obj = FavoriteBooking(customer=user, hotel=hotel, tour=tour, type=_type)
        fav_obj.save()
        return True

    @classmethod
    def remove_favorite(cls, user, _type=BookingType.HOTEL, hotel=None, tour=None):
        fav_obj = FavoriteBooking.objects.filter(customer=user, hotel=hotel, tour=tour).first()
        if fav_obj:
            fav_obj.delete()
            return True
        return False
