from django.urls import path

from users.views import (
    userAppPassCreate,
    userAppPassDel,
    userAppPassEdit,
    userAppPassList,
    userAppPassToggleActive,
    userAppPassUpdate,
    # userVacations,
    # userVacationsDelete,
    # userVacationsEnd,
    # userVacationsEdit,
    toggleUserOoO,
)

urlpatterns = [
    path("ooo/", toggleUserOoO, name="user-ooo"),
    path("apps/", userAppPassList, name="user-apps-list"),
    path("apps/new/", userAppPassCreate, name="user-apps-create"),
    path("apps/<pk>", userAppPassToggleActive, name="user-apps-toggle"),
    path("apps/<pk>/reset", userAppPassUpdate, name="user-apps-reset"),
    path("apps/<pk>/edit", userAppPassEdit, name="user-apps-edit"),
    path("apps/<pk>/del", userAppPassDel, name="user-apps-delete"),
    # path("leave", userVacations, name="user-vacations-list"),
    # path("leave/<pk>", userVacationsEdit, name="user-vacations-edit"),
    # path("leave/<pk>/end", userVacationsEnd, name="user-vacations-end"),
    # path("leave/<pk>/del", userVacationsDelete, name="user-vacations-del"),
    # path("leave/new/", userVacationsEdit, name="user-vacations-new"),
]