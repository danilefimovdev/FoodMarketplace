from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from accounts.models import User, UserProfile


class CustomUserAdmin(UserAdmin):
    fieldsets = ()
    filter_horizontal = ()
    list_filter = ()
    ordering = ('-date_joined', )
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active', )


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
