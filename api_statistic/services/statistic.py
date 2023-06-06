from datetime import timedelta

from django.db.models import Sum

from api_booking.models import Booking
from api_user.statics import RoleData
from common.constants.api_booking import BookingStatus


class StatisticService:
    @classmethod
    def get_revenue_statistic(cls, user,
                              start_date=None,
                              end_date=None):
        user_role = user.role.id
        if user_role.hex == RoleData.PARTNER.value.get('id'):
            tour_statistic = Booking.objects.filter(booking_item__tour__owner__id=user.id,
                                                    status__in=[BookingStatus.PAID, BookingStatus.COMPLETED])
            hotel_statistic = Booking.objects.filter(booking_item__room__hotel__owner__id=user.id,
                                                     status__in=[BookingStatus.PAID, BookingStatus.COMPLETED])
        else:
            tour_statistic = Booking.objects.filter(booking_item__tour__isnull=False,
                                                    status__in=[BookingStatus.PAID, BookingStatus.COMPLETED])
            hotel_statistic = Booking.objects.filter(booking_item__room__isnull=False,
                                                     status__in=[BookingStatus.PAID, BookingStatus.COMPLETED])

        date_statistic = []
        if start_date and end_date:
            total_tour = tour_statistic.filter(created_at__date__range=[start_date, end_date]) \
                                        .aggregate(total_price=Sum("booking_item__tour__price"))
            total_hotel = hotel_statistic.filter(created_at__date__range=[start_date, end_date]) \
                                         .aggregate(total_price=Sum("booking_item__room__price"))
            date = start_date
            while date <= end_date:
                tour = tour_statistic.filter(created_at__date=date) \
                    .aggregate(total_price=Sum("booking_item__tour__price"))
                hotel = hotel_statistic.filter(created_at__date=date) \
                    .aggregate(total_price=Sum("booking_item__room__price"))
                date_statistic.append({
                    "day": date,
                    "tour": tour['total_price'] or 0,
                    "hotel": hotel['total_price'] or 0
                })
                date = date + timedelta(days=1)
        else:
            total_tour = tour_statistic.aggregate(total_price=Sum("booking_item__tour__price"))
            total_hotel = hotel_statistic.aggregate(total_price=Sum("booking_item__room__price"))

        total_tour = total_tour['total_price'] or 0
        total_hotel = total_hotel['total_price'] or 0

        response = {
            "total_tour": int(total_tour),
            "total_hotel": int(total_hotel),
            "details": date_statistic,
        }
        return response
