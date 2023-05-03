from api_tour.models import Tour
from api_tour.serializers import TourSerializer, SortTourSerializer
from api_user.permission import UserPermission
from base.views import BaseViewSet


class TourViewSet(BaseViewSet):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "list": [],
        "retrieve": []
    }

    serializer_map = {
        'list': SortTourSerializer,
    }

