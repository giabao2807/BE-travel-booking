import os
from datetime import datetime, time

from django.db.models import Q, QuerySet, Sum, Value, Avg, Min, Max
from django.db.models.functions import Collate

from api_booking.consts import BookingType
from api_booking.models import BookingReview, Booking
from api_general.consts import DatetimeFormatter
from api_general.models import Coupon, Image
from api_general.services import Utils, RecommendService
from api_tour.models import Tour, TourImage
from api_user.models import Profile
from api_user.statics import RoleData
from base.services import CloudinaryService
from common.constants.api_booking import BookingStatus
from common.constants.api_tour import TourImage as ConstImage
from dotenv import load_dotenv

load_dotenv()


class TourService:
    @classmethod
    def get_top_tour_recommend_sys(cls):
        tour_ids = RecommendService.get_recommend_top_tour(None)
        return Tour.objects.filter(id__in=tour_ids)

    @classmethod
    def recommend_for_user(cls, user: Profile, limit):
        num = limit or 6
        tour_ids = RecommendService.get_recommend_tour_for_user(user, num)
        return Tour.objects.filter(id__in=tour_ids)

    @classmethod
    def refresh_image(cls, tour):
        tour_images = TourImage.objects.filter(tour=tour)
        image_ids = [tour_image.image.id for tour_image in tour_images]
        images = Image.objects.filter(id__in=image_ids)
        for img in images:
            img.delete()

    @classmethod
    def get_filter_query(cls, request):
        name = request.query_params.get("name", "")
        city_id = request.query_params.get("city_id", None)
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        sort_by = request.query_params.get("sort_by", "asc")
        price_range = request.query_params.get("price_range", None)  # "0-200000"

        order_by = "price" if sort_by == "asc" else "-price"

        start_date = Utils.safe_str_to_date(start_date, DatetimeFormatter.YYMMDD)
        end_date = Utils.safe_str_to_date(end_date, DatetimeFormatter.YYMMDD)

        tour_queryset = Tour.objects.all()

        if start_date and end_date:
            tour_queryset = cls.filter_by_date(start_date, end_date)

        if name:
            name = Collate(Value(name.strip()), "utf8mb4_general_ci")

        filter_args = dict()
        filter_args.update(is_active=True)
        if city_id:
            filter_args.update(city__id=city_id)

        if price_range:
            prices = price_range.split('-')
            min_price_range = int(prices[0])
            max_price_range = int(prices[1])
            filter_args.update(price__gte=min_price_range)
            filter_args.update(price__lte=max_price_range)

        top_tours = tour_queryset \
            .filter(name__icontains=name, **filter_args) \
            .order_by(order_by) \
            # .order_by("-created_at")

        return top_tours

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
        data['owner'] = request.user.id
        tour_images_link = []

        if cover_picture:
            image_link = CloudinaryService.upload_image(cover_picture, os.getenv('CLOUDINARY_TOUR_FOLDER'))
            data['cover_picture'] = image_link
        else:
            data['cover_picture'] = ConstImage.tour_image_default

        if tour_images:
            tour_images_link = CloudinaryService.upload_list_image(tour_images, os.getenv("CLOUDINARY_TOUR_FOLDER"))
        return data, tour_images_link

    @classmethod
    def list_tour_manage(cls, user: Profile, filter_name):
        queryset = Tour.objects.filter(name__icontains=filter_name)
        if user.role.id.hex == RoleData.PARTNER.value.get('id'):
            tour_ft = Q(owner=user)
            queryset = queryset.filter(tour_ft)
        return queryset

    @classmethod
    def count_num_review(cls, tour: Tour):
        return BookingReview.objects.filter(booking__booking_item__tour=tour).count()

    @classmethod
    def check_deactive_tour(cls, tour: Tour, user: Profile):
        is_valid = True
        if user.role.id.hex == RoleData.ADMIN.value.get('id'):
            return True
        if tour.owner.id != user.id:
            return False
        bookings = Booking.objects.filter(booking_item__tour=tour)
        for booking in bookings:
            if booking.status == BookingStatus.PAID:
                return False
        return is_valid

    @classmethod
    def get_current_coupon(cls, tour_id: str) -> Coupon:
        current_date = datetime.now().date()
        base_ft = Q(
            is_active=True,
            start_date__lte=datetime.combine(current_date, time.max),
            end_date__gte=datetime.combine(current_date, time.min)
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
