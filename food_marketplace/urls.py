from django.contrib import admin
from django.urls import path, include
from food_marketplace import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls, name=admin),
    path('', views.home, name='home'),
    path('', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
