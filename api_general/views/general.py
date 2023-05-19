from rest_framework.response import Response

from api_general.services import GeneralService
from api_tour.serializers import CardTourSerializer
from base.views import BaseViewSet


class GeneralViewSet(BaseViewSet):
    permission_classes = []

    permission_map = {
        "list_general": [],
        "retrieve": []
    }

    serializer_map = {
        'list': CardTourSerializer,
    }
