from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from users.models import CustomUser, Departments


class SuperUserCheck(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class StaffUserCheck(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class UserEditView(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'nickname', 'phone',]
    success_url = reverse_lazy('home')
    template_name = 'users/edit_user.html'

    def get_object(self, queryset=None):
        return self.request.user


class AdminUserView(StaffUserCheck, ListView):
    model = CustomUser

    def get_queryset(self, *args, **kwargs):
        qs = super(AdminUserView, self).get_queryset(*args, **kwargs)
        qs = qs.exclude(is_superuser=True)
        return qs


class AdminUserEdit(StaffUserCheck, UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'nickname', 'phone', 'departments']

    def get_object(self, *args, **kwargs):
        user = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        return user

    def get_success_url(self, *args, **kwargs):
        return reverse("users-view")


class DepartmentNew(StaffUserCheck, CreateView):
    model = Departments
    fields = ['department', 'description']

    success_url = reverse_lazy("dpts-view")
    template_name = 'users/department_form.html'


class DepartmentView(StaffUserCheck, ListView):
    model = Departments


class DepartmentEdit(StaffUserCheck, UpdateView):
    model = Departments
    fields = ['department', 'description']


    def get_object(self, *args, **kwargs):
        dpt = get_object_or_404(Department, pk=self.kwargs['pk'])
        return dpt

    def get_success_url(self, *args, **kwargs):
        return reverse("dpts-view")
