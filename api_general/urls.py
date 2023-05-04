from rest_framework import routers


app_name = 'api_general'
router = routers.SimpleRouter(trailing_slash=True)

# router.register(r'', TourViewSet, basename='tour')

urlpatterns = router.urls
