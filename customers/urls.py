from django.urls import path
from accounts import views as account_views
from customers import views

urlpatterns = [
    path('', account_views.dashboard, name='customer'),
    path('profile/', views.c_profile, name='c-profile'),
    ]
