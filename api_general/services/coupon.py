from typing import List, Union

from django.db import transaction

from api_general.models import Coupon
from api_hotel.models import HotelCoupon, Hotel
from api_tour.models import TourCoupon, Tour
from api_user.models import Profile
from api_user.statics import RoleData


class CouponService:
    @classmethod
    def get_coupon_by_user(cls, user: Profile):
        if user.role.id.hex == RoleData.ADMIN.value.get('id'):
            queryset = Coupon.objects.all().order_by("-created_at")
        else:
            queryset = Coupon.objects.filter(created_by=user)
        return queryset

    @classmethod
    def refresh_hotel_tour_coupons(cls, coupon, partner_ids):
        hotel_coupons: List[HotelCoupon] = []
        tour_coupons: List[TourCoupon] = []
        hotel_ids, tour_ids = cls.get_hotel_and_tour_by_partners(partner_ids)

        if hotel_ids:
            for _hotel_id in hotel_ids:
                hotel_coupons.append(HotelCoupon(hotel_id=_hotel_id, coupon=coupon))
            HotelCoupon.objects.bulk_create(hotel_coupons)
        if tour_ids:
            for _tour_id in tour_ids:
                tour_coupons.append(TourCoupon(tour_id=_tour_id, coupon=coupon))
            TourCoupon.objects.bulk_create(tour_coupons)

    @classmethod
    def get_hotel_and_tour_by_partners(cls, partner_ids: List):
        hotel_ids = Hotel.objects.filter(owner_id__in=partner_ids).values_list("id", flat=True)
        tour_ids = Tour.objects.filter(owner_id__in=partner_ids).values_list("id", flat=True)

        return hotel_ids, tour_ids
