from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api_booking.models.review import BookingReview
import os
from dotenv import load_dotenv

from api_booking.services import BookingReviewService

load_dotenv()


class BookingReviewSerializer(ModelSerializer):
    owner_avatar = serializers.CharField(source="booking.customer.avatar")
    owner_first_name = serializers.CharField(source="booking.customer.first_name")
    owner_last_name = serializers.CharField(source="booking.customer.last_name")

    class Meta:
        model = BookingReview
        fields = "__all__"

    def to_representation(self, instance):
        data = super(BookingReviewSerializer, self).to_representation(instance)
        owner_name = " ".join([data.pop("owner_first_name"), data.pop("owner_last_name")])
        owner_data = dict(
            id=str(data.get("booking.customer")),
            avatar=data.pop("owner_avatar") or os.getenv("DEFAULT_CUSTOMER_AVATAR", ""),
            name=owner_name
        )
        data["owner"] = owner_data

        return data


class CreateBookingReviewSerializer(ModelSerializer):
    class Meta:
        model = BookingReview
        fields = ('content', 'title', 'booking', 'rate', 'owner')

    def validate(self, attrs):
        booking = attrs.get("booking", None)

        if booking:
            BookingReviewService.validate_review_booking(booking_id=booking.id, raise_exception=True)

        return attrs

