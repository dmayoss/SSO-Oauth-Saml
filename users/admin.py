from django.contrib import admin
# from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Department


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    add_fieldsets = (
        (None, {"fields": (('email', 'password1', 'password2', 'first_name', 'last_name',)),}),
    )

    fieldsets = (
        (None, {"fields": (('email', 'password', 'first_name', 'last_name',)),}),
        (None, {"fields": (('department', 'phone',)),}),
        (None, {"fields": (('groups', 'user_permissions', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login')),}),
    )

    search_fields = ['email', 'first_name', 'last_name']
    list_display = ['email', 'first_name', 'last_name']
    ordering = [ 'email', ]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department', 'description')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
