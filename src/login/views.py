from logging import getLogger
from threading import Thread

# logger = getLogger(__name__)
logger = getLogger("sso")
# logger.setLevel(logging.INFO)

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

# from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password

# from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django_otp.decorators import otp_required

from login.forms import customSetPasswordForm, customPasswordChangeForm
from login.models import OneTimePasswords
from sso.helper import get_client_ip, send_reset_email_with_otp
from sso.tokens import account_activation_token
from users.forms import customUserResetPasswordForm
from users.models import CustomUser, PrivacyAgreement


# @login_required
@otp_required
def CustomUserPasswordUpdate(request):
    if request.method == "POST":
        form = customPasswordChangeForm(request.user, request.POST)
        ip = get_client_ip(request)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password was successfully updated!")
            return redirect("password-change-done")
        else:
            messages.error(request, "Please correct the error below.")
            logger.info("Password Reset FAILED for {} from {}".format(request.user, ip))
    else:
        form = customPasswordChangeForm(request.user)

    context = {
        "form": form,
    }

    return render(request, "accounts/password_reset.html", context)


# @login_required
@otp_required
def CustomUserPasswordUpdated(request):
    ip = get_client_ip(request)
    logger.info("Password Reset by {} from {}".format(request.user, ip))
    template = loader.get_template("accounts/password_reset_complete.html")
    context = {}
    return HttpResponse(template.render(context, request))


def CustomUserPasswordReset(request):
    """
    This view needs to be accessible to unauthenticated users
    currently only searches email field (i.e. only emaildomain.com)
    silently continues on non-existent email
    """
    if request.method == "POST":
        form = customUserResetPasswordForm(request.POST)
        ip = get_client_ip(request)
        if form.is_valid():
            template = loader.get_template("accounts/password_reset_done.html")
            email = form.cleaned_data["email"]
            logger.info(
                "Password reset being attempted for {} from {}".format(email, ip)
            )
            forker(checkUserEmail, email)
        else:
            logger.info("Password Reset attempt FAILED from {} (bad form)".format(ip))
            template = loader.get_template(
                "edit_form.html"
            )  # invalid form --> do again
    else:
        template = loader.get_template("edit_form.html")
        form = customUserResetPasswordForm()

    context = {
        "form": form,
    }

    return HttpResponse(template.render(context, request))


def CustomUserPasswordReseted(request):
    """
    This view is the only one accessible to unauthenticated users
    currently only searches email field (i.e. only emaildomain.com)
    silently continues on non-existent email
    """
    template = loader.get_template(
        "accounts/password_reset_done.html"
    )  # first of all, valid form --> done
    context = {}
    return HttpResponse(template.render(context, request))


def TokenReset(request, uidb64, token):
    """
    This view uses the SetPasswordForm
    This is for when the user is either first setting, or otherwise resetting, their password.
    """

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except Exception as e:
        logger.warn("{}".format(e))
        raise PermissionDenied

    if account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = customSetPasswordForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, "Your password was successfully updated!")
                return redirect("password-change-done")
            else:
                messages.error(request, "Please correct the error below.")
        else:
            form = customSetPasswordForm(user)

        context = {
            "form": form,
        }

        return render(request, "accounts/password_reset.html", context)
    else:
        return redirect("password-reset")


def forker(target, data):
    """
    Uses threads to check for a valid email.
    Return value doesn't matter.
    We wont ever .join() these
    """
    t = Thread(target=target, args=(data,))
    t.start()
    return True


def checkUserEmail(email):
    """
    if the email is worth checking, try to get it. if we find it, send a reset for it
    """

    if "@emaildomain.com" not in email:
        logger.info("Password Reset attempt REJECTED for email {}".format(email))
        return None
    else:
        userlist = CustomUser.objects.filter(email=email)
        userobj = next(iter(userlist), None)
        if userobj:
            logger.info("Doing Password Reset for user {}".format(userobj))
            return DoEmailReset(userobj)
        else:
            logger.info(
                "Password Reset attempted for email {}, user did not exist".format(
                    email
                )
            )


def DoEmailReset(user, altEmail=False, displayOTP=False):
    """
    Only be here if we're from the internal view, so we already know the email is fine
    """

    try:
        otpass = OneTimePasswords.generate_pass()
        othash = make_password(otpass)
        otobj, created = OneTimePasswords.objects.get_or_create(
            user=user, defaults={"password": othash}
        )
        if not created:
            otobj.password = othash
        otobj.save()
        return send_reset_email_with_otp(user, otpass, altEmail, displayOTP)
    except Exception as e:
        return None
