from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_hotel.models import HotelReview
import os
from dotenv import load_dotenv

load_dotenv()


class HotelReviewSerializer(ModelSerializer):
    owner_avatar = serializers.CharField(source="owner.avatar")
    owner_first_name = serializers.CharField(source="owner.first_name")
    owner_last_name = serializers.CharField(source="owner.last_name")

    class Meta:
        model = HotelReview
        fields = "__all__"

    def to_representation(self, instance):
        data = super(HotelReviewSerializer, self).to_representation(instance)
        owner_name = " ".join([data.pop("owner_first_name"), data.pop("owner_last_name")])
        owner_data = dict(
            id=str(data.get("owner")),
            avatar=data.pop("owner_avatar") or os.getenv("DEFAULT_CUSTOMER_AVATAR", ""),
            name=owner_name
        )
        data["owner"] = owner_data

        return data
