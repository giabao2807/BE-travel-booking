from api_tour.models import Tour
from api_tour.serializers import TourSerializer
from base.views import BaseViewSet


class TourViewSet(BaseViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
