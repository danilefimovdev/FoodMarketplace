from django.urls import path, include
from accounts import views

urlpatterns = [
    path('', views.my_account),
    path('registerUser/', views.register_user, name='register-user'),
    path('registerVendor/', views.registerVendor, name='register-vendor'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('my_account/', views.my_account, name='my-account'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>', views.activate_user, name='activate'),

    path('forgot_password/', views.forgot_password, name='forgot-password'),
    path('reset_password_validate/<uidb64>/<token>', views.reset_password_validate, name='reset-password-validate'),
    path('reset_password/', views.reset_password, name='reset-password'),

    path('vendor/', include('vendors.urls')),
    path('customer/', include('customers.urls')),
]