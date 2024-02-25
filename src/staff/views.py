from logging import getLogger

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.views.generic.list import ListView
from django_otp.decorators import otp_required
from oauth2_provider.models import AccessToken
from oauth2_provider.views.generic import ProtectedResourceView
from two_factor.views.mixins import OTPRequiredMixin

# logger = getLogger(__name__)
logger = getLogger("sso")
# logger.setLevel(logging.INFO)

from login.views import DoEmailReset

from sso.helper import (
    get_client_ip,
    send_reset_email,
    send_reset_email_with_otp,
    send_reset_sms,
    user_is_hr,
    user_is_staff,
)

from staff.forms import (
    DepartmentEditForm,
    DepartmentMemberForm,
    HRUserEditForm,
    UserNewForm,
    UserRoleMapEditForm,
    UserRoleMapForm,
    userResetMethodForm,
    StaffUserSearchForm,
)

from users.models import AppPasswords, CustomUser, Departments, UserRoleMap


# check user privileges
class HRUserCheck(UserPassesTestMixin):
    def test_func(self):
        return user_is_hr(self.request.user)


# check for elevated user (is_staff or is_superuser)
class StaffUserCheck(UserPassesTestMixin):
    def test_func(self):
        return user_is_staff(self.request.user)


class UserListView(LoginRequiredMixin, OTPRequiredMixin, HRUserCheck, FormMixin, ListView):
    model = CustomUser
    form_class = StaffUserSearchForm
    
    def get_queryset(self, *args, **kwargs):
        email = self.request.GET.get('email', '')
        user_type= self.request.GET.getlist('user_type', '')
        active = self.request.GET.get('active', 'off')

        qs = super(UserListView, self).get_queryset(*args, **kwargs)

        # superusers should NEVER normally be used/available/editable
        qs = qs.exclude(is_superuser=True)

        if email:
            qs = qs.filter(email__icontains=email)  # searching for 'mod' is not going to be useful...

        if user_type:
            qs = qs.filter(user_type__in=user_type)
        else:
            qs = qs.filter(user_type="USER")  # hard coded all normal users

        if active == "on":
            qs = qs.filter(is_active=True)  # nothing else matters

        return qs.order_by('email')


class UserNewView(LoginRequiredMixin, OTPRequiredMixin, HRUserCheck, CreateView):
    model = CustomUser
    template_name = "edit_form.html"
    form_class = UserNewForm
    success_url = reverse_lazy("staff-user-list")


class HRUserEditView(LoginRequiredMixin, OTPRequiredMixin, HRUserCheck, UpdateView):
    model = CustomUser
    template_name = "edit_form.html"
    form_class = HRUserEditForm
    success_url = reverse_lazy("staff-user-list")


class DepartmentsNewView(
    LoginRequiredMixin, OTPRequiredMixin, StaffUserCheck, CreateView
):
    model = Departments
    form_class = DepartmentEditForm
    template_name = "edit_form.html"
    success_url = reverse_lazy("staff-dpts-list")


class DepartmentsDeleteView(
    LoginRequiredMixin, OTPRequiredMixin, StaffUserCheck, DeleteView
):
    model = Departments
    fields = ["id"]
    success_url = reverse_lazy("staff-dpts-list")


class DepartmentsEditView(
    LoginRequiredMixin, OTPRequiredMixin, StaffUserCheck, UpdateView
):
    model = Departments
    form_class = DepartmentEditForm
    template_name = "edit_form.html"
    success_url = reverse_lazy("staff-dpts-list")


class DepartmentsListView(LoginRequiredMixin, OTPRequiredMixin, HRUserCheck, ListView):
    model = Departments


@login_required
@otp_required
def departmentMembers(request, pk):
    """
    - if you're an ADMIN in the department, or something other than a normal USER user_type,
      you can add/remove department USERS including other department ADMINS.
    - if not, this view will fail
    """
    department = get_object_or_404(Departments, pk=pk)

    try:
        role_map = get_object_or_404(
            UserRoleMap, department=department, user=request.user
        )
    except:
        role_map = None

    # effectively, if role IS admin or user_type NOT 'USER'
    # will have to update if we get more user_type's
    if not role_map:
        if not user_is_hr(request.user):
            raise PermissionError("Permission Denied")
    else:
        if not (user_is_hr(request.user) or role_map.role == "ADMIN"):
            raise PermissionError("Permission Denied")

    if request.method == "POST":
        form = DepartmentMemberForm(request.POST)
        if form.is_valid():
            ip = get_client_ip(request)
            role_user = form.cleaned_data["user"]
            action = form.cleaned_data["action"]

            logger.info(
                "[Group Admin {}] : [{}] role in {} for {} from {}".format(
                    request.user, action, department, role_user, ip
                )
            )

            if action == "ADD":  # see FORM_ACTION_CHOICES
                obj, created = UserRoleMap.objects.get_or_create(
                    user=role_user,
                    department=department,
                    defaults={
                        "role": "USER",  # see ROLES_CHOICES
                    },
                )
            elif action == "DEL":
                try:
                    UserRoleMap.objects.get(
                        user=role_user,
                        department=department,
                    ).delete()
                except Exception as e:
                    messages.error(
                        request, "Error deleting User Role Map: {}".format(e)
                    )
    else:
        form = DepartmentMemberForm()

    context = {
        "department": department,
        "form": form,
    }

    template = loader.get_template("users/department_manage.html")
    return HttpResponse(template.render(context, request))


@user_passes_test(user_is_hr)
@otp_required
def HRUserPasswordReset(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    ip = get_client_ip(request)

    if request.method == "POST":
        form = userResetMethodForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data["method"]

            if method == "EMAIL":
                result = DoEmailReset(user)
            elif method == "ALTEMAIL":
                result = DoEmailReset(user, altEmail=True)
            elif method == "SHOWEMAIL":
                result = DoEmailReset(user, displayOTP=True)
            elif method == "SHOWALT":
                result = DoEmailReset(user, altEmail=True, displayOTP=True)
            else:
                raise PermissionDenied

            messages.success(
                request, "Password reset requested for user {}: {}".format(user, result)
            )
            logger.info(
                "[HR] : Password Reset requested for user {} by user {} from {}".format(
                    user, request.user, ip
                )
            )
    else:
        form = userResetMethodForm()

    context = {
        "form": form,
    }

    template = loader.get_template("edit_form.html")
    return HttpResponse(template.render(context, request))


@user_passes_test(user_is_hr)
@otp_required
def userRoleDepartment(request):
    if request.method == "POST":
        ip = get_client_ip(request)
        form = UserRoleMapForm(request.POST)
        if form.is_valid():
            obj, created = UserRoleMap.objects.update_or_create(
                user=form.cleaned_data["user"],
                role=form.cleaned_data["role"],
                department=form.cleaned_data["department"],
            )
            if created:
                logger.info(
                    "[HR] : role created for {} in {} by {} from {}".format(
                        obj.user, obj.department, request.user, ip
                    )
                )
            else:
                logger.info(
                    "[HR] : role updated for {} in {} by {} from {}".format(
                        obj.user, obj.department, request.user, ip
                    )
                )
    else:
        form = UserRoleMapForm()

    context = {
        "object_list": UserRoleMap.objects.all(),
        "form": form,
        "editform": UserRoleMapEditForm,
    }

    template = loader.get_template("users/user_dept_map_list.html")
    return HttpResponse(template.render(context, request))


@user_passes_test(user_is_hr)
@otp_required
def userRoleMgmtEdit(request, pk):
    if request.method == "POST":
        form = UserRoleMapEditForm(request.POST)
        if form.is_valid():
            ip = get_client_ip(request)
            obj = get_object_or_404(UserRoleMap, pk=pk)
            obj.role = form.cleaned_data["role"]
            obj.save()
            logger.info(
                "[HR] : role in {} updated for {} by {} from {}".format(
                    obj.department, obj.user, request.user, ip
                )
            )
    return redirect(userRoleDepartment)


@user_passes_test(user_is_hr)
@otp_required
def userRoleMgmtDelete(request, pk):
    UserRoleMap.objects.get(pk=pk).delete()
    return redirect(userRoleDepartment)


@user_passes_test(user_is_hr)
@otp_required
def toggleUserActive(request, pk):
    obj = get_object_or_404(CustomUser, pk=pk)

    if obj.is_active == False:
        obj.is_active = True
    else:
        obj.is_active = False

    obj.save()

    return redirect("staff-user-list")


@user_passes_test(user_is_hr)
@otp_required
def toggleUserUnix(request, pk):
    obj = get_object_or_404(CustomUser, pk=pk)

    if obj.unixlogin == False:
        obj.unixlogin = True
    else:
        obj.unixlogin = False

    obj.save()

    return redirect("staff-user-list")


@login_required
@otp_required
@user_passes_test(user_is_hr)
def staffAppPassDel(request, pk):
    obj = get_object_or_404(CustomUser, pk=pk)
    ip = get_client_ip(request)
    try:
        obj.apppasswords_set.all().delete()
    except Exception as e:
        messages.error(request, "Error deleting app passwords: {}".format(e))
    else:
        messages.success(request, "Deleted all app passwords for user {}".format(obj))
        logger.info(
            "[HR]: all app passwords for {} deleted by {} from {}".format(
                obj, request.user, ip
            )
        )

    return redirect("staff-user-list")
