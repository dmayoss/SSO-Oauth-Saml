from django.urls import path

from .views import SignUpView, UserEditView, AdminUserView, AdminUserEdit
from user_sessions.views import SessionDeleteView, SessionListView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('edit/', UserEditView.as_view(), name="edit-user-profile"),
    path('view/', AdminUserView.as_view(), name="users-view"),
    path('sessions/', SessionListView.as_view(), name="session-list-view"),
    path('sessions/<pk>/delete', SessionDeleteView.as_view(), name="session-del-view"),
    path('<pk>/', AdminUserEdit.as_view(), name="users-edit"),
]
