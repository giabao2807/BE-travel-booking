from rest_framework import routers

from api_booking.views.booking import BookingViewSet

app_name = 'api_booking'
router = routers.SimpleRouter(trailing_slash=True)
router.register(r'', BookingViewSet, basename='booking')

urlpatterns = router.urls
