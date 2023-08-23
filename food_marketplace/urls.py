from django.contrib import admin
from django.urls import path, include

from accounts import views as account_views
from food_marketplace import views
from django.conf.urls.static import static
from django.conf import settings
from marketplace import views as marketplace_views

urlpatterns = [
    path('admin/', admin.site.urls, name=admin),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('cart/', marketplace_views.cart, name='cart'),

    path('search/', marketplace_views.search, name='search'),

    path('checkout/', marketplace_views.checkout, name='checkout'),

    path('orders/', include('orders.urls')),
    # path('schedule_mail/', account_views.schedule_mail),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
