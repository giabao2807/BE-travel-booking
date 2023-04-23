from rest_framework import routers


app_name = 'api_tour'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'role', RoleViewSet, basename='role')

urlpatterns = router.urls
