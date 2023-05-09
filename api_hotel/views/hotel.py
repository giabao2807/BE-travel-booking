from api_hotel.models import Hotel
from api_hotel.serializers import HotelSerializer
from api_user.permission import UserPermission
from base.views import BaseViewSet


class HotelViewSet(BaseViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "list": [],
        "retrieve": []
    }
