from rest_framework import routers

from api_tour.views import TourViewSet

app_name = 'api_tour'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'', TourViewSet, basename='tour')

urlpatterns = router.urls
