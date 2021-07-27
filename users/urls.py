from django.urls import path

from .views import SignUpView, UserEditView, AdminUserView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('edit/', UserEditView.as_view(), name="edit-user-profile"),
    path('view/', AdminUserView.as_view(), name="users-view"),
]
