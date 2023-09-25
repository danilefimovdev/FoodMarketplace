from django.urls import path
from vendors import views
from accounts import views as account_views

urlpatterns = [
    path('', account_views.vendor_dashboard, name='vendor'),
    path('profile/', views.v_profile, name='v-profile'),
    path('menu-builder/', views.menu_builder, name='menu-builder'),
    path('menu-builder/categories/<str:slug>', views.fooditems_by_category, name='fooditems-by-category'),

    # Category CRUD
    path('menu-builder/category/add/', views.add_category, name='add-category'),
    path('menu-builder/category/edit/<str:slug>', views.edit_category, name='edit-category'),
    path('menu-builder/category/delete/<str:slug>', views.delete_category, name='delete-category'),

    # Food CRUD
    path('menu-builder/food/add/', views.add_food, name='add-food'),
    path('menu-builder/food/edit/<str:slug>', views.edit_food, name='edit-food'),
    path('menu-builder/food/delete/<str:slug>', views.delete_food, name='delete-food'),

    # Opening Hour CRUD
    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove-opening-hours'),

    path('order-detail/<int:order_number>/', views.order_detail, name='v-order-detail'),
    path('orders/', views.my_orders, name='v-my-orders'),
]