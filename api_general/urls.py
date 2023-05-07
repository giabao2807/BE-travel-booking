from rest_framework import routers

from api_general.views import CityViewSet

app_name = 'api_general'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'city', CityViewSet, basename='city')

urlpatterns = router.urls
