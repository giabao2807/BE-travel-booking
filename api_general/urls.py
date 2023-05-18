from rest_framework import routers

from api_general.views import CityViewSet, CouponViewSet, GeneralViewSet

app_name = 'api_general'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'city', CityViewSet, basename='city')
router.register(r'coupon', CouponViewSet, basename='coupon')
router.register(r'', GeneralViewSet, basename='general')

urlpatterns = router.urls
