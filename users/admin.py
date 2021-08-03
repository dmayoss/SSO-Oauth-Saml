from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Departments


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    add_fieldsets = (
        (None, {"fields": (('email', 'password1', 'password2', 'first_name', 'last_name',)),}),
    )

    fieldsets = (
        (None, {"fields": (('email', 'password',)),}),
        (None, {"fields": (('first_name', 'last_name', 'nickname')),}),
        (None, {"fields": (('departments', 'phone',)),}),
        (None, {"fields": (('groups', 'user_permissions', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login')),}),
    )

    search_fields = ['email', 'first_name', 'last_name', 'nickname']
    list_display = ['email', 'username', 'first_name', 'last_name', 'nickname']
    ordering = [ 'email', ]


class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('department', 'description')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Departments, DepartmentsAdmin)
