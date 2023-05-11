from rest_framework import routers

from api_hotel.views import HotelViewSet, RoomViewSet

app_name = 'api_hotel'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'', HotelViewSet, basename='hotel')
router.register(r'room', RoomViewSet, basename='room')

urlpatterns = router.urls
