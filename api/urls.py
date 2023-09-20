import rest_framework.routers
from django.urls import include, path

from api.views import TokenAuthenticationViewSet, UsersViewSet, RestaurantsViewSet, CartViewSet, \
    FoodItemsViewSet

router = rest_framework.routers.DefaultRouter()
router.register(prefix='auth', viewset=TokenAuthenticationViewSet, basename='auth')
router.register(prefix='users', viewset=UsersViewSet, basename='users')
router.register(prefix='restaurants', viewset=RestaurantsViewSet, basename='restaurants')
router.register(prefix='fooditems', viewset=FoodItemsViewSet, basename='fooditems')
router.register(prefix='my_cart', viewset=CartViewSet, basename='my_cart')


urlpatterns = [
    ]

urlpatterns += router.urls
