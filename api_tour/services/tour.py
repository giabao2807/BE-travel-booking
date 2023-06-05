import os
from datetime import datetime

from django.db.models import Q, QuerySet, Sum

from api_booking.consts import BookingType
from api_booking.models import BookingReview
from api_general.models import Coupon
from api_general.services import Utils
from api_tour.models import Tour
from api_user.models import Profile
from base.services import ImageService
from common.constants.api_booking import BookingStatus
from common.constants.api_tour import TourImage
from dotenv import load_dotenv

load_dotenv()


class TourService:
    @classmethod
    def filter_by_date(cls, start_date: datetime, end_date: datetime) -> QuerySet:
        diff_dates = (end_date - start_date).days + 1
        tour_ft = Q(is_active=True) & Q(total_days__lt=f"{diff_dates + 1} ngày")
        tour_qs = Tour.objects.filter(tour_ft).order_by("-total_days")

        print(Utils.get_raw_query(tour_qs))

        return tour_qs

    @classmethod
    def init_data_tour(cls, request):
        data = request.data.dict()
        cover_picture = request.FILES.get('cover_picture')
        tour_images = request.FILES.getlist("tour_images")
        owner_id = request.user.id
        data['owner'] = owner_id

        if cover_picture:
            image_link = ImageService.upload_image(cover_picture, os.getenv('CLOUDINARY_TOUR_FOLDER'))
            data['cover_picture'] = image_link
        else:
            data['cover_picture'] = TourImage.tour_image_default

        if tour_images:
            tour_images_link = ImageService.upload_list_image(tour_images, os.getenv("CLOUDINARY_TOUR_FOLDER"))
        return data, tour_images_link

    @classmethod
    def list_tour_by_partner(cls, owner: Profile):
        tour_ft = Q(owner=owner)
        return Tour.objects.filter(tour_ft)

    @classmethod
    def count_num_review(cls, tour: Tour):
        return BookingReview.objects.filter(booking__booking_item__tour=tour).count()

    @classmethod
    def get_current_coupon(cls, tour_id: str) -> Coupon:
        current_date = datetime.now().date()
        base_ft = Q(
            is_active=True,
            start_date__date__lte=current_date,
            end_date__date__gte=current_date
        )

        for_all_coupon_ft = Q(for_all=True)
        selected_tours_coupon_ft = Q(for_all=False, tour_coupons__tour_id=tour_id)
        tour_coupon_ft = base_ft & (for_all_coupon_ft | selected_tours_coupon_ft)
        coupon = Coupon.objects.filter(tour_coupon_ft).order_by("-discount_percent").first()

        return coupon

    @classmethod
    def get_booked_tour_amounts(cls, start_date: datetime, tour_id: str = ""):
        valid_booking_status = [BookingStatus.PAID, BookingStatus.UNPAID]
        tour_ft = Q(booking_item__booking__start_date__date=start_date.date()) & \
                     Q(booking_item__booking__type=BookingType.TOUR) & \
                     Q(booking_item__booking__status__in=valid_booking_status) & \
                     Q(is_active=True)

        if tour_id:
            tour_ft &= Q(id=tour_id)
        booked_tour_mapping = dict(
            Tour.objects.filter(tour_ft).values("id")
                .annotate(booked_tour_amount=Sum("booking_item__quantity"))
                .values_list("id", "booked_tour_amount")
        )

        return booked_tour_mapping

    @classmethod
    def get_available_group_size(cls, tour: Tour, start_date: datetime) -> int:
        booked_amount_mapping = cls.get_booked_tour_amounts(start_date, tour.id)
        booked_amount = booked_amount_mapping.get(tour.id, 0)

        return tour.group_size - booked_amount
