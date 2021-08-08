from django.urls import path

from .views import UserEditView, UserEditProfileView, UserKeysListView, UserKeysEditView, UserKeysNewView, UserKeysDeleteView, UserKeysActView
from user_sessions.views import SessionDeleteView, SessionListView


urlpatterns = [
    path('edit', UserEditProfileView.as_view(), name="user-edit-profile"),
    path('edit/<pk>', UserEditView.as_view(), name="user-edit"),
    path('keys', UserKeysListView.as_view(), name="user-keys-list"),
    path('keys/<pk>', UserKeysEditView.as_view(), name="user-keys-edit"),
    path('keys/<pk>/del', UserKeysDeleteView.as_view(), name="user-key-del"),
    path('keys/<pk>/use', UserKeysActView.as_view(), name="user-key-use"),
    path('keys/new/', UserKeysNewView.as_view(), name="user-keys-new"),
    path('sessions/', SessionListView.as_view(), name="sessions-list"),
    path('sessions/<pk>/delete', SessionDeleteView.as_view(), name="sessions-del"),
]
