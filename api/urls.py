from django.urls import path
from rest_framework import routers

from api.views import TokenAuthenticationViewSet, UsersViewSet, RestaurantsViewSet, CartViewSet, \
    FoodItemsViewSet, ProfileViewSet

router = routers.SimpleRouter()
router.register(prefix='auth', viewset=TokenAuthenticationViewSet, basename='auth')
router.register(prefix='users', viewset=UsersViewSet, basename='users')
router.register(prefix='restaurants', viewset=RestaurantsViewSet, basename='restaurants')
router.register(prefix='fooditems', viewset=FoodItemsViewSet, basename='fooditems')
router.register(prefix='my_cart', viewset=CartViewSet, basename='my_cart')
router.register(prefix='account', viewset=ProfileViewSet, basename='account')

urlpatterns = [
    ]

urlpatterns += router.urls



