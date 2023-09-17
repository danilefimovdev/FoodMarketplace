import rest_framework.routers
from django.urls import include, path

from api.views import TokenAuthenticationViewSet, UsersViewSet

router = rest_framework.routers.SimpleRouter()
router.register(prefix='auth', viewset=TokenAuthenticationViewSet, basename='auth')
router.register(prefix='users', viewset=UsersViewSet, basename='users')


urlpatterns = [
    ]

urlpatterns += router.urls
