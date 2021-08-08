from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from users.models import CustomUser, Departments, UnixGroups
from .forms import StaffUserEditForm


class SuperUserCheck(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class StaffUserCheck(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class StaffUserListView(StaffUserCheck, ListView):
    model = CustomUser

    def get_queryset(self, *args, **kwargs):
        qs = super(StaffUserListView, self).get_queryset(*args, **kwargs)
        qs = qs.exclude(is_superuser=True)
        return qs


class StaffUserEditView(StaffUserCheck, UpdateView):
    model = CustomUser
    template_name = 'staff/edit_user.html'
    form_class = StaffUserEditForm

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse("staff-users-list")


class DepartmentsNewView(StaffUserCheck, CreateView):
    model = Departments
    fields = ['department', 'description']

    template_name = 'edit_form.html'
    success_url = reverse_lazy("dpts-list")


class DepartmentsListView(StaffUserCheck, ListView):
    model = Departments


class DepartmentsEditView(StaffUserCheck, UpdateView):
    model = Departments
    template_name = 'edit_form.html'

    fields = ['department', 'description']

    def get_object(self, *args, **kwargs):
        dpt = get_object_or_404(Departments, pk=self.kwargs['pk'])
        return dpt

    def get_success_url(self, *args, **kwargs):
        return reverse("dpts-list")


class UnixGroupsNewView(StaffUserCheck, CreateView):
    model = UnixGroups
    fields = ['group_name', 'description']

    template_name = 'edit_form.html'
    success_url = reverse_lazy("unix-groups-list")


class UnixGroupsListView(StaffUserCheck, ListView):
    model = UnixGroups


class UnixGroupsEditView(StaffUserCheck, UpdateView):
    model = UnixGroups
    template_name = 'edit_form.html'

    fields = ['group_name', 'description']

    def get_object(self, *args, **kwargs):
        dpt = get_object_or_404(UnixGroups, pk=self.kwargs['pk'])
        return dpt

    def get_success_url(self, *args, **kwargs):
        return reverse("unix-groups-list")
