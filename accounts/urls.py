from django.urls import path
from accounts import views

urlpatterns = [
    path('registerUser/', views.registerUser, name='register-user'),
    path('registerVendor/', views.registerVendor, name='register-vendor'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my_account/', views.my_account, name='my-account'),
    path('dashboard/', views.dashboard, name='dashboard'),
]