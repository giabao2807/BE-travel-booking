from rest_framework import status
from rest_framework.response import Response

from api_booking.models.review import BookingReview
from api_booking.serializers import BookingReviewSerializer, CreateBookingReviewSerializer
from api_user.permission import UserPermission
from base.views import BaseViewSet


class ReviewViewSet(BaseViewSet):
    queryset = BookingReview.objects.all()
    serializer_class = BookingReviewSerializer
    permission_classes = [UserPermission]

    permission_map = {
        "list": []
    }

    serializer_map = {
        "create": CreateBookingReviewSerializer
    }

    def create(self, request, *args, **kwargs):
        request_body = request.data
        request_body["owner"] = request.user.id

        serializer = self.get_serializer(data=request_body)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

