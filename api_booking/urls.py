from rest_framework import routers


app_name = 'api_booking'
router = routers.SimpleRouter(trailing_slash=True)

urlpatterns = router.urls