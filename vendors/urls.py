from django.urls import path
from vendors import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.dashboard, name='vendor'),
    path('profile/', views.v_profile, name='v-profile'),
]
