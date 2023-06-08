from datetime import timedelta

from django.db.models import Sum

from api_booking.models import Booking
from api_hotel.models import Hotel
from api_tour.models import Tour
from api_user.models import Profile
from api_user.statics import RoleData
from common.constants.api_booking import BookingStatus
import collections


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

    @classmethod
    def get_box_dashboard(cls, user):
        if user.role.id.hex == RoleData.PARTNER.value.get('id'):
            res = cls.get_partner_box_dashboard(user)
        else:
            res = cls.get_admin_box_dashboard()
        return res

    @classmethod
    def get_admin_box_dashboard(cls):
        accept_status = [BookingStatus.PAID, BookingStatus.COMPLETED]
        error_status = [BookingStatus.UNPAID, BookingStatus.CANCELED]
        booking_success = Booking.objects.filter(status__in=accept_status).count()
        booking_error = Booking.objects.filter(status__in=error_status).count()
        tour = Tour.objects.filter().count()
        hotel = Hotel.objects.filter().count()
        customer = Profile.objects.filter(role__id=RoleData.CUSTOMER.value.get('id')).count()
        partner = Profile.objects.filter(role__id=RoleData.PARTNER.value.get('id')).count()

        res = [
            {"key": "booking_success", "title": "Booking", "color": "#ffa39e",
             "value": booking_success, "rateString": "thành công"},
            {"key": "booking_error", "title": "Booking", "color": "#91caff",
             "value": booking_error, "rateString": "gián đoạn"},
            {"key": "tour", "title": "Tổng số tour", "color": "#ff7a45",
             "value": tour, "rateString": "hiện tại"},
            {"key": "hotel", "title": "Tổng số hotel", "color": "#135200",
             "value": hotel, "rateString": "hiện tại"},
            {"key": "customer", "title": "Tổng khách hàng", "color": "#87CEFA",
             "value": customer, "rateString": "hiện tại"},
            {"key": "partner", "title": "Tổng đối tác", "color": "#87CEFA",
             "value": partner, "rateString": "hiện tại"}
        ]

        return res

    @classmethod
    def get_partner_box_dashboard(cls, user):
        accept_status = [BookingStatus.PAID, BookingStatus.COMPLETED]
        error_status = [BookingStatus.UNPAID, BookingStatus.CANCELED]
        booking_success = Booking.objects.filter(booking_item__tour__owner__id=user.id,
                                                 status__in=accept_status).count() \
                            + Booking.objects.filter(booking_item__room__hotel__owner__id=user.id,
                                                     status__in=accept_status).count()
        booking_error = Booking.objects.filter(booking_item__tour__owner__id=user.id,
                                                 status__in=error_status).count() \
                            + Booking.objects.filter(booking_item__room__hotel__owner__id=user.id,
                                                     status__in=error_status).count()
        tour = Tour.objects.filter(owner__id=user.id).count()
        hotel = Hotel.objects.filter(owner__id=user.id).count()
        tours = Booking.objects.filter(booking_item__tour__owner__id=user.id)
        hotels = Booking.objects.filter(booking_item__room__hotel__owner__id=user.id)
        total_cus = set([tour.customer.id for tour in tours] + [hotel.customer.id for hotel in hotels])
        res = [
            {"key": "booking_success", "title": "Booking", "color": "#ffa39e",
             "value": booking_success, "rateString": "thành công"},
            {"key": "booking_error", "title": "Booking", "color": "#91caff",
             "value": booking_error, "rateString": "gián đoạn"},
            {"key": "tour", "title": "Tổng số tour", "color": "#ff7a45",
             "value": tour, "rateString": "hiện tại"},
            {"key": "hotel", "title": "Tổng số hotel", "color": "#135200",
             "value": hotel, "rateString": "hiện tại"},
            {"key": "customer", "title": "Tổng khách hàng", "color": "#87CEFA",
             "value": len(total_cus), "rateString": "hiện tại"}
        ]

        return res

    @classmethod
    def get_potential_customers(cls, user):
        if user.role.id.hex == RoleData.PARTNER.value.get('id'):
            customers = cls.get_potential_customers_for_partner(user)
        else:
            customers = cls.get_potential_customers_sys()
        return customers

    @classmethod
    def get_potential_customers_for_partner(cls, user):
        accept_status = [BookingStatus.PAID, BookingStatus.COMPLETED]
        tours = Booking.objects.filter(booking_item__tour__owner__id=user.id,
                                       status__in=accept_status)
        hotels = Booking.objects.filter(booking_item__room__hotel__owner__id=user.id,
                                        status__in=accept_status)
        return cls.get_potential_customer_by_tours_hotel(tours, hotels)

    @classmethod
    def get_potential_customers_sys(cls):
        accept_status = [BookingStatus.PAID, BookingStatus.COMPLETED]
        tours = Booking.objects.filter(status__in=accept_status)
        hotels = Booking.objects.filter(status__in=accept_status)
        return cls.get_potential_customer_by_tours_hotel(tours, hotels)

    @classmethod
    def get_potential_customer_by_tours_hotel(cls, tours, hotels):
        customer_ids = [tour.customer.id for tour in tours] + [hotel.customer.id for hotel in hotels]
        customer_count = collections.Counter(customer_ids)
        customer_sorted = sorted(customer_count.items(), key=lambda x: x[1], reverse=True)
        customer_ids_rs = [item[0] for item in customer_sorted]
        customers = Profile.objects.filter(id__in=customer_ids_rs)
        potential_customers = []
        for cus_id in customer_ids_rs:
            for cus in customers:
                if cus.id == cus_id:
                    potential_customers.append(cus)
                    break
        return potential_customers