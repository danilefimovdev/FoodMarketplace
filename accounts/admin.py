from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User, UserProfile


class CustomUserAdmin(UserAdmin):
    fieldsets = ()
    filter_horizontal = ()
    list_filter = ()
    ordering = ('-date_joined', )
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active', 'is_subscribed')


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
