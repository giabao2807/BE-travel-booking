from django.db.models import Q

from api_booking.consts import BookingType
from api_booking.models import Booking, FavoriteBooking
from api_booking.serializers import BookingSerializer, CUBookingSerializer, ListBookingSerializer, \
    ListHotelFavoriteSerializer, ListTourFavoriteSerializer
from api_general.services import Utils
from api_user.permission import UserPermission, PartnerPermission
from api_user.statics import RoleData
from base.views import BaseViewSet
from common.constants.base import HttpMethod


class FavoriteViewSet(BaseViewSet):
    queryset = FavoriteBooking.objects.all()
    permission_classes = [UserPermission]

    def list(self, request, *args, **kwargs):
        _type = request.query_params.get("type")
        _type = Utils.safe_int(_type)

        booking_ft = Q(type=_type) & Q(customer=request.user)
        self.serializer_class = ListHotelFavoriteSerializer if _type == BookingType.HOTEL else ListTourFavoriteSerializer

        self.queryset = FavoriteBooking.objects.filter(booking_ft).order_by("-created_at")

        return super().list(request, *args, **kwargs)
