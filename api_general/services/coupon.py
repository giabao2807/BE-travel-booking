from typing import List, Union

from django.db import transaction

from api_general.models import Coupon
from api_hotel.models import HotelCoupon
from api_tour.models import TourCoupon


class CouponService:
    @classmethod
    @transaction.atomic
    def create(cls, coupon_data: dict, hotel_ids, tour_ids) -> Coupon:
        for_all = coupon_data.get("for_all", False)

        coupon = Coupon(**coupon_data)
        coupon.save()

        if not for_all:
            cls.refresh_hotel_tour_coupons(coupon, hotel_ids, tour_ids)

        return coupon

    @classmethod
    @transaction.atomic
    def update_related(cls, coupon: Coupon, coupon_data: dict):
        for_all = coupon_data.get("for_all", False)
        hotel_ids = coupon_data.get("hotel_ids", [])
        tour_ids = coupon_data.get("tour_ids", [])

        coupon.hotel_coupons.all().delete()
        coupon.tour_coupons.all().delete()
        if not for_all:
            cls.refresh_hotel_tour_coupons(coupon, hotel_ids, tour_ids)

    @classmethod
    def refresh_hotel_tour_coupons(cls, coupon, hotel_ids, tour_ids):
        hotel_coupons: List[HotelCoupon] = []
        tour_coupons: List[TourCoupon] = []
        for _hotel_id in hotel_ids:
            hotel_coupons.append(HotelCoupon(hotel_id=_hotel_id, coupon=coupon))
        for _tour_id in tour_ids:
            tour_coupons.append(TourCoupon(tour_id=_tour_id, coupon=coupon))
        HotelCoupon.objects.bulk_create(hotel_coupons)
        TourCoupon.objects.bulk_create(tour_coupons)

    @classmethod
    def sync_object_coupons(cls, coupon, current_object_ids: List[str], request_object_ids: List[str], model_class):
        object_pk_field = "hotel_id" if model_class == HotelCoupon else "tour_id"
        outdated_object_ids: List[str] = list(set(current_object_ids) - set(request_object_ids))
        new_object_ids: List[str] = list(set(request_object_ids) - set(current_object_ids))

        new_object_coupons: List[model_class] = [
            model_class(**{"coupon": coupon, object_pk_field: _object_id})
            for _object_id in new_object_ids
        ]
        model_class.objects.bulk_create(new_object_coupons)
        model_class.objects.filter(**{"coupon": coupon, f"{object_pk_field}__in": outdated_object_ids}).delete()
