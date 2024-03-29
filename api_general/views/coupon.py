from rest_framework import status
from rest_framework.response import Response

from api_general.models import Coupon
from api_general.serializers import CouponSerializer
from api_general.serializers.coupon import CUCouponSerializer
from api_general.services.coupon import CouponService
from api_user.permission import PartnerPermission
from api_user.statics import RoleData
from base.exceptions import BoniException
from base.exceptions.base import ErrorType
from base.views import BaseViewSet


class CouponViewSet(BaseViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [PartnerPermission]
    serializer_map = {
        "create": CUCouponSerializer,
        "update": CUCouponSerializer
    }

    def create(self, request, *args, **kwargs):
        request_data = request.data
        request_data["created_by"] = request.user.id
        if RoleData.is_partner(request.user):
            request.data["for_all"] = False

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        coupon = self.get_object()
        if RoleData.is_partner(request.user):
            if coupon.created_by != request.user:
                raise BoniException(ErrorType.GENERAL, ["Bạn không là chủ mã giảm này"])
        coupon.delete()
        return Response({"message": "Xoá thành công coupon!"}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user = request.user
        self.queryset = CouponService.get_coupon_by_user(user)

        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        coupon = self.get_object()
        request_data = request.data
        request_data["created_by"] = request.user.id
        if RoleData.is_partner(request.user):
            if coupon.created_by != request.user:
                raise BoniException(ErrorType.GENERAL, ["Bạn không là chủ mã giảm này"])
            request.data["for_all"] = False
        return super().update(request, *args, **kwargs)
