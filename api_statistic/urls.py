from rest_framework import routers

from api_statistic.views import StatisticViewSet

app_name = 'api_statistic'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'', StatisticViewSet, basename='statistic')

urlpatterns = router.urls
