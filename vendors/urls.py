from django.urls import path
from vendors import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.dashboard, name='vendor'),
    path('profile/', views.v_profile, name='v-profile'),
    path('menu-builder/', views.menu_builder, name='menu-builder'),
    path('menu-builder/categories/<int:pk>', views.fooditems_by_category, name='fooditems-by-category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add-category'),
    path('menu-builder/category/edit/<int:pk>', views.edit_category, name='edit-category'),
    path('menu-builder/category/delete/<int:pk>', views.delete_category, name='delete-category'),

    # Food CRUD
    path('menu-builder/food/add/', views.add_food, name='add-food'),
    path('menu-builder/food/edit/<int:pk>', views.edit_food, name='edit-food'),
    path('menu-builder/food/delete/<int:pk>', views.delete_food, name='delete-food'),

    # Opening Hour CRUD
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove-opening-hours'),

]