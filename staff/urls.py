from django.urls import path

from .views import StaffUserListView, StaffUserEditView
from .views import DepartmentsListView, DepartmentsEditView, DepartmentsNewView
from .views import UnixGroupsListView, UnixGroupsEditView, UnixGroupsNewView


urlpatterns = [
    path('users', StaffUserListView.as_view(), name="staff-users-list"),
    path('users/<pk>', StaffUserEditView.as_view(), name="staff-users-edit"),
    path('departments', DepartmentsListView.as_view(), name="dpts-list"),
    path('departments/<pk>', DepartmentsEditView.as_view(), name="dpts-edit"),
    path('departments/new/', DepartmentsNewView.as_view(), name="dpts-new"),
    path('groups', UnixGroupsListView.as_view(), name="unix-groups-list"),
    path('groups/<pk>', UnixGroupsEditView.as_view(), name="unix-groups-edit"),
    path('groups/new/', UnixGroupsNewView.as_view(), name="unix-groups-new"),
]
