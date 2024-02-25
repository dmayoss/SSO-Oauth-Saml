from django.urls import path

from .views import (
    CustomUserPasswordReset,
    CustomUserPasswordReseted,
    CustomUserPasswordUpdate,
    CustomUserPasswordUpdated,
    TokenReset,
)

urlpatterns = [
    path("pass", CustomUserPasswordUpdate, name="password-change"),
    path("pass/done", CustomUserPasswordUpdated, name="password-change-done"),
    path("reset", CustomUserPasswordReset, name="password-reset"),
    path("reset/done", CustomUserPasswordReseted, name="password-reset-done"),
    path("reset/<uidb64>/<token>/", TokenReset, name="password-reset-confirm"),
]
