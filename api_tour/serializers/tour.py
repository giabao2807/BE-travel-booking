from rest_framework.serializers import ModelSerializer

from api_user.models import Tour


class TourSerializer(ModelSerializer):

    class Meta:
        model = Tour
        fields = "__all__"
