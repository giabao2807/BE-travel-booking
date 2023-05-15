from typing import List, Union

from django.db import transaction

from api_general.models import Coupon
from api_hotel.models import HotelCoupon
from api_tour.models import TourCoupon


class CouponService:
    @classmethod
    @transaction.atomic
    def create(cls, coupon_data: dict) -> Coupon:
        hotel_ids = coupon_data.pop("hotel_ids", [])
        tour_ids = coupon_data.pop("tour_ids", [])
        hotel_coupons: List[HotelCoupon] = []
        tour_coupons: List[TourCoupon] = []

        coupon = Coupon(**coupon_data)
        coupon.save()
        for _hotel_id in hotel_ids:
            hotel_coupons.append(HotelCoupon(hotel_id=_hotel_id, coupon=coupon))
        for _tour_id in tour_ids:
            tour_coupons.append(TourCoupon(tour_id=_tour_id, coupon=coupon))

        HotelCoupon.objects.bulk_create(hotel_coupons)
        HotelCoupon.objects.bulk_create(tour_coupons)

        return coupon

    @classmethod
    @transaction.atomic
    def update_related(cls, coupon: Coupon, coupon_data: dict):
        hotel_ids = coupon_data.pop("hotel_ids", [])
        tour_ids = coupon_data.pop("tour_ids", [])
        current_hotel_ids: List[str] = coupon.hotel_coupons.values_list("hotel_id", flat=True)
        current_tour_ids: List[str] = coupon.tour_coupons.values_list("tour_id", flat=True)

        cls.sync_object_coupons(coupon, current_hotel_ids, hotel_ids, model_class=HotelCoupon)
        cls.sync_object_coupons(coupon, current_tour_ids, tour_ids, model_class=TourCoupon)

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
