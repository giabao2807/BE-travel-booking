from api_tour.serializers import SortTourSerializer
from api_user.permission import UserPermission
from base.views import BaseViewSet


class GeneralViewSet(BaseViewSet):
    permission_classes = [UserPermission]

    permission_map = {
        "list_general": [],
        "retrieve": []
    }

    serializer_map = {
        'list': SortTourSerializer,
    }



