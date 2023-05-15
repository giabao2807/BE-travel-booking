from api_general.models import Coupon
from api_general.serializers import CouponSerializer
from api_general.serializers.coupon import CUCouponSerializer
from api_user.permission import PartnerPermission
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

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request_data = request.data
        request_data["created_by"] = request.user.id

        return super().update(request, *args, **kwargs)
