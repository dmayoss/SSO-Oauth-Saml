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
from users.forms import (
    UserAppPassEditForm,
    UserEditForm,
    UserNewForm,
    UserRoleMapEditForm,
    UserRoleMapForm,
    userResetMethodForm,
    UserVacationForm,
)
from users.models import AppPasswords, CustomUser, Departments, UserRoleMap, UserVacations


@login_required
@otp_required
def toggleUserOoO(request):
    if request.user.is_ooo == False:
        request.user.is_ooo = True
    else:
        request.user.is_ooo = False

    request.user.save()

    return redirect("home")


@login_required
@otp_required
def userVacations(request):
    context = {
        "form": UserVacationForm()
    }
    
    template = loader.get_template("users/user_vacations.html")

    return HttpResponse(template.render(context, request))


@login_required
@otp_required
def userVacationsEdit(request, pk=None):
    # if there's no pk, it's a new one
    if pk:
        obj = get_object_or_404(UserVacations, pk=pk)
        if obj.user != request.user:
            raise PermissionDenied

        # you can't edit vacations that are over
        # although I'll let you delete them
        if obj.end_date.date() < timezone.now().date():
            return redirect("user-vacations-list")
    else:
        obj = None

    if request.method == "POST":
        form = UserVacationForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
        
            # I really should just clean the form...
            if obj.start_date > obj.end_date:
                temp = obj.end_date
                obj.end_date = obj.start_date
                obj.start_date = temp
            obj.save()
            return redirect("user-vacations-list")
        else:
            context = {
                    "form": form
            }
    else:
        # we're in GET
        if obj:
            context = { 
                "form": UserVacationForm(instance=obj)
            }
        else:
            context = { 
                "form": UserVacationForm()
            }
    
    template = loader.get_template("edit_form.html")

    return HttpResponse(template.render(context, request))


def userVacationsDelete(request, pk):
    obj = get_object_or_404(UserVacations, pk=pk)

    if obj.user != request.user:
        raise PermissionDenied

    obj.delete()

    return redirect("user-vacations-list")


def userVacationsEnd(request, pk):
    obj = get_object_or_404(UserVacations, pk=pk)

    if obj.user != request.user:
        raise PermissionDenied

    obj.end_date = timezone.now()
    obj.save()

    return redirect("user-vacations-list")


@login_required
@otp_required
def userAppPassList(request):
    context = {
        "object_list": request.user.apppasswords_set.all(),
        "form": UserAppPassEditForm(),
    }

    template = loader.get_template("users/app_pass_manage.html")
    return HttpResponse(template.render(context, request))


@login_required
@otp_required
def userAppPassCreate(request):
    if request.method == "POST":
        form = UserAppPassEditForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data["application"]
            app_entry = form.cleaned_data["name"]
            app_pass = AppPasswords.generate_pass()

            # first check if it already exists, if so we replace
            obj, created = AppPasswords.objects.get_or_create(
                user=request.user,
                name=app_entry,  # from the app-name list/type
                application=app_name,  # user-defined name
                defaults={
                    "username": request.user.email,
                    "password": make_password(app_pass),
                    "active": True,  # by default
                },
            )

            if not created:
                obj.password = make_password(app_pass)
                obj.save()

            newpass = {
                "name": obj.name,
                "application": obj.get_application_display(),
                "pass": app_pass,
            }

            messages.success(
                request,
                "User Application {} for {} Password Created.".format(
                    obj.name, obj.get_application_display()
                ),
            )
        else:
            newpass = None
    else:
        newpass = None

    context = {
        "newpass": newpass,
    }

    template = loader.get_template("users/app_pass_manage.html")
    return HttpResponse(template.render(context, request))


@login_required
@otp_required
def userAppPassUpdate(request, pk):
    obj = get_object_or_404(AppPasswords, pk=pk)

    if obj.user != request.user:
        raise PermissionDenied

    app_pass = AppPasswords.generate_pass()
    obj.password = make_password(app_pass)
    obj.save()

    messages.success(
        request,
        "User application password '{}' for {} successfully edited".format(
            obj.name, obj.get_application_display()
        ),
    )

    newpass = {
        "name": obj.name,
        "application": obj.get_application_display(),
        "pass": app_pass,
    }

    context = {
        "newpass": newpass,
    }

    template = loader.get_template("users/app_pass_manage.html")
    return HttpResponse(template.render(context, request))


@login_required
@otp_required
def userAppPassEdit(request, pk):
    obj = get_object_or_404(AppPasswords, pk=pk)

    if request.method == "POST":
        form = UserAppPassEditForm(request.POST)
        if form.is_valid():
            obj.name = form.cleaned_data["name"]
            try:
                obj.save()
            except Exception as e:
                messages.error(
                    request, "User application password update failed. {}".format(e)
                )
            else:
                messages.success(
                    request,
                    "User application password '{}' for {} successfully edited".format(
                        obj.name, obj.get_application_display()
                    ),
                )
        else:
            messages.error(
                request,
                "User application password '{}' for {} NOT updated".format(
                    obj.name, obj.get_application_display()
                ),
            )

    return redirect("home")


@login_required
@otp_required
def userAppPassToggleActive(request, pk):
    obj = get_object_or_404(AppPasswords, pk=pk)

    if obj.user != request.user:
        raise PermissionDenied

    if obj.active == False:
        obj.active = True
        messages.info(
            request,
            "User Application password for {} set active".format(
                obj.get_application_display()
            ),
        )
    else:
        obj.active = False
        messages.info(
            request,
            "User Application password for {} set inactive".format(
                obj.get_application_display()
            ),
        )

    try:
        obj.save()
    except Exception as e:
        messages.error(request, "error updating app password")

    return redirect("home")


@login_required
@otp_required
def userAppPassDel(request, pk):
    obj = get_object_or_404(AppPasswords, pk=pk)

    if obj.user != request.user:
        raise PermissionDenied
    else:
        messages.info(
            request,
            "User application password {} for {} has been deleted".format(
                obj.name, obj.get_application_display()
            ),
        )
        obj.delete()

    return redirect("home")


@login_required
def home(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                messages.error(request, "Error updating User: {}".format(e))
            else:
                messages.success(request, "Updated User")

            return redirect("home")

    context = {
        "form": UserEditForm(initial=model_to_dict(request.user)),
        "vacation_form": UserVacationForm()
        # 'newappform': UserAppPassEditForm(),
        # 'shellform': ldapShellForm(initial=model_to_dict(request.user.ldapuser)),
        # 'sshkeyform': ldapSSHKeyForm(),
    }

    template = loader.get_template("home.html")
    return HttpResponse(template.render(context, request))


"""
we're now using the user pk as gitlab id
adding otpview doesn't work
this is what php sends:

$email = $user;
$usernamearray = explode("@", $user);
$username = str_replace(".", " ", $usernamearray[0]);

// Create user info from the user-id`
$resp = array("name" => $username,"username" => $username,"id" => (int)$assoc_id,"state" => "active","email" => $email,"login" => $user);
"""


class GitLabApiUserView(ProtectedResourceView, ListView):
    # https://docs.gitlab.com/ee/api/users.html#list-current-user-for-normal-users
    def get(self, *args, **kwargs):
        if not self.request.user.is_active:
            raise PermissionDenied

        r = {
            "id": self.request.user.pk,
            "state": "active",
            "email": self.request.user.email,
            "login": self.request.user.uid,
            "name": self.request.user.get_full_name(),
            "username": self.request.user.username,
        }

        return JsonResponse(r)


class GiteaApiUserView(ListView):
    ''' by itself this doesn't do anything but return a JSON about the user attached to the access_token '''
    def get(self, *args, **kwargs):
        access_token = self.request.GET.get('access_token', None)

        if not access_token:
            raise PermissionDenied

        obj = get_object_or_404(AccessToken, token=access_token)

        if not obj.user.is_active:
            raise PermissionDenied

        r = {
            "id": obj.user.pk,
            "state": "active",
            "email": obj.user.email,
            "login": obj.user.uid,
            "name": obj.user.get_full_name(),
            "username": obj.user.username,
            }

        return JsonResponse(r)
