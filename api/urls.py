from django.urls import path
from rest_framework import routers

from api.views import TokenAuthenticationViewSet, UsersViewSet, RestaurantsViewSet, CartViewSet, \
    FoodItemsViewSet, ProfileViewSet, CustomerOrdersViewSet, VendorOrdersViewSet

router = routers.SimpleRouter()
router.register(prefix='auth', viewset=TokenAuthenticationViewSet, basename='auth')
router.register(prefix='users', viewset=UsersViewSet, basename='users')
router.register(prefix='restaurants', viewset=RestaurantsViewSet, basename='restaurants')
router.register(prefix='fooditems', viewset=FoodItemsViewSet, basename='fooditems')


customer_urlpaterns = [
    path('customers/<str:username>/orders/', CustomerOrdersViewSet.as_view({'get': 'list'})),
    path('customers/<str:username>/orders/<str:order_number>/', CustomerOrdersViewSet.as_view({'get': 'retrieve'})),
    path('customers/<str:username>/profile/', ProfileViewSet.as_view(
            {'get': 'profile', 'put': 'profile', 'patch': 'profile'})
         ),
    path('customers/<str:username>/my_cart/', CartViewSet.as_view({'get': 'list'})),
    path('customers/<str:username>/my_cart/<int:pk>/', CartViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy', 'put': 'update'})
         ),
]

vendor_urlpatterns = [
    path('vendors/<str:vendor_slug>/orders/', VendorOrdersViewSet.as_view({'get': 'list'})),
    path('vendors/<str:vendor_slug>/orders/<str:order_number>/', VendorOrdersViewSet.as_view({'get': 'retrieve'})),
    path('vendors/<str:vendor_slug>/profile/', ProfileViewSet.as_view(
        {'get': 'profile', 'put': 'profile', 'patch': 'profile'})
         ),
    ]

urlpatterns = [
    ]

urlpatterns += router.urls
urlpatterns.extend(customer_urlpaterns)
urlpatterns.extend(vendor_urlpatterns)



