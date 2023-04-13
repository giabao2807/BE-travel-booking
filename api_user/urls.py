from rest_framework import routers

from .views import RoleViewSet, ProfileViewSet, AuthViewSet

app_name = 'api_user'
router = routers.SimpleRouter(trailing_slash=True)

router.register(r'role', RoleViewSet, basename='role')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'', ProfileViewSet, basename='user')

urlpatterns = router.urls
