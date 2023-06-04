from django.urls import path
from accounts import views as account_views
from customers import views

urlpatterns = [
    path('', account_views.dashboard, name='customer'),
    path('profile/', views.c_profile, name='c-profile'),
    path('my_orders/', views.my_orders, name='c-my-orders'),
    path('order-details/<int:order_number>/', views.order_details, name='c-order-details'),
    ]
