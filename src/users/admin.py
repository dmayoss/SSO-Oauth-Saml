from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.sessions.models import Session

from .models import AppPasswords, CustomUser, Departments, PersistentId, UserRoleMap, UserVacations


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "email",
                        "password1",
                        "password2",
                        "first_name",
                        "last_name",
                    )
                ),
            },
        ),
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "email",
                        "password",
                    )
                ),
            },
        ),
        (
            None,
            {
                "fields": (("first_name", "last_name", "phone")),
            },
        ),
        (
            None,
            {
                "fields": (("unixlogin",)),
            },
        ),
        (
            None,
            {
                "fields": (("date_joined", "last_login")),
            },
        ),
        (
            None,
            {
                "fields": (("is_superuser", "is_staff", "is_active", "user_type")),
            },
        ),
        (
            None,
            {
                "fields": (("groups",)),
            },
        ),
    )

    search_fields = ["email", "first_name", "last_name", "user_type", "original_email"]
    list_display = [
        "email",
        "original_email",
        "user_type",
        "username",
        "first_name",
        "last_name",
        "phone",
        "is_active",
    ]
    ordering = [
        "email",
    ]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("department", "description")


class PersistentIdAdmin(admin.ModelAdmin):
    list_display = ("user", "persistent_id", "recipient_id", "created")
    list_filter = ("created",)


class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()

    list_display = ["session_key", "_session_data", "expire_date"]


class VacationAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date")


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Departments, DepartmentAdmin)
admin.site.register(AppPasswords)
admin.site.register(UserRoleMap)
admin.site.register(PersistentId, PersistentIdAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(UserVacations, VacationAdmin)
