from api_hotel.models import Hotel
from api_tour.serializers import TourSerializer
from base.views import BaseViewSet


class HotelViewSet(BaseViewSet):
    queryset = Hotel.objects.all()
    serializer_class = TourSerializer
    permission_classes = []
