from django.urls import path

from staff.views import (
    DepartmentsDeleteView,
    DepartmentsEditView,
    DepartmentsListView,
    DepartmentsNewView,
    departmentMembers,
    HRUserEditView,
    HRUserPasswordReset,
    staffAppPassDel,
    toggleUserActive,
    toggleUserUnix,
    UserListView,
    UserNewView,
    userRoleDepartment,
    userRoleMgmtDelete,
    userRoleMgmtEdit,
)

urlpatterns = [
    path("list/", UserListView.as_view(), name="staff-user-list"),
    path("new/", UserNewView.as_view(), name="staff-user-new"),
    path("<pk>", HRUserEditView.as_view(), name="staff-user-edit"),
    path("<pk>/toggleactive", toggleUserActive, name="staff-user-toggle"),
    path("<pk>/toggleunix", toggleUserUnix, name="staff-user-toggle-unix"),
    path("<pk>/resetpass", HRUserPasswordReset, name="staff-user-reset-pass"),
    path("<pk>/delapps", staffAppPassDel, name="staff-user-del-app"),
    path("dpts/list/", DepartmentsListView.as_view(), name="staff-dpts-list"),
    path("dpts/new/", DepartmentsNewView.as_view(), name="staff-dpts-new"),
    path("dpts/<pk>", DepartmentsEditView.as_view(), name="staff-dpts-edit"),
    path("dpts/<pk>/manage", departmentMembers, name="staff-dpts-mgmt"),
    path("dpts/<pk>/del", DepartmentsDeleteView.as_view(), name="staff-dpts-del"),
    path("roles/", userRoleDepartment, name="staff-role-manage"),
    path("roles/<pk>", userRoleMgmtEdit, name="staff-role-mgmt-edit"),
    path("roles/<pk>/del", userRoleMgmtDelete, name="staff-role-mgmt-del"),
]