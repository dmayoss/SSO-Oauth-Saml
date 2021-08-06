from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Departments, UnixGroups, UnixShells, UserKeys


class UserKeysAdmin(admin.TabularInline):
     model = UserKeys


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    inlines = [UserKeysAdmin,]

    add_fieldsets = (
        (None, {"fields": (('email', 'password1', 'password2', 'first_name', 'last_name',)),}),
    )

    fieldsets = (
        (None, {"fields": (('email', 'password',)),}),
        (None, {"fields": (('first_name', 'last_name', 'nickname',)),}),
        (None, {"fields": (('unixname', 'unixlogin',)),}),
        (None, {"fields": (('homedir', 'shell', 'unixgroups',)),}),
        (None, {"fields": (('is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login')),}),
        (None, {"fields": (('departments', 'phone',)),}),
    )

    search_fields = ['email', 'first_name', 'last_name', 'nickname']
    list_display = ['email', 'username', 'first_name', 'last_name']
    ordering = [ 'email', ]


class DepartmentsAdmin(admin.ModelAdmin):
    list_display = ('department', 'description')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Departments, DepartmentsAdmin)
admin.site.register(UnixGroups)
admin.site.register(UnixShells)
admin.site.register(UserKeys)
