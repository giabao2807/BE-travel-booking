from api_booking.models import Booking
from api_booking.models.review import BookingReview
from api_hotel.models import Hotel
from api_tour.models import Tour
from base.exceptions import BoniException
from base.exceptions.base import ErrorType
from common.constants.api_booking import BookingStatus


class BookingReviewService:
    @classmethod
    def get_tour_review(cls, tour: Tour):
        tour_booking_ids = Booking.objects.all().filter(booking_item__tour__id=tour.id).values("id")
        return BookingReview.objects.filter(booking__id__in=tour_booking_ids)

    @classmethod
    def get_hotel_review(cls, hotel: Hotel):
        hotel_booking_ids = Booking.objects.all().filter(booking_item__room__hotel__id=hotel.id).values("id")
        return BookingReview.objects.filter(booking__id__in=hotel_booking_ids)

    @classmethod
    def validate_review_booking(cls, booking_id, **kwargs) -> bool:
        """

        @param room_id:
        @param kwargs:
        @return:
        """
        is_valid: bool = True
        raise_exception: bool = kwargs.get("raise_exception", False)

        booking = Booking.objects.filter(id=booking_id).first()
        if booking:
            if booking.status != BookingStatus.COMPLETED:
                is_valid = False
                if raise_exception:
                    raise BoniException(ErrorType.REQUIRED, ["Trải nghiệm booking"])
        else:
            is_valid = False
            if raise_exception:
                raise BoniException(ErrorType.DEACTIVATED_VN, ["Booking"])

        return is_valid
