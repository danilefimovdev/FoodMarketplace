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
]
