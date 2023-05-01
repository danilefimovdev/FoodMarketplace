from django.urls import path
from vendors import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.dashboard, name='vendor'),
    path('profile/', views.v_profile, name='v-profile'),
    path('menu-builder/', views.menu_builder, name='menu-builder'),
    path('menu-builder/categories/<int:pk>', views.fooditems_by_category, name='fooditems-by-category'),

]
