from rest_framework import routers

from api_hotel.views import HotelViewSet, RoomTypeViewSet

app_name = 'api_hotel'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'', HotelViewSet, basename='hotel')
router.register(r'room_type', RoomTypeViewSet, basename='room_type')

urlpatterns = router.urls
