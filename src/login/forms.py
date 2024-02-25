import datetime

from django import forms

# from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from login.models import OneTimePasswords


class customSetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class customPasswordChangeForm(customSetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """

    error_messages = {
        **customSetPasswordForm.error_messages,
        "password_incorrect": _(
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password


class customSetPasswordForm(customSetPasswordForm):
    """
    A customised form that lets a user change their password by entering an OTP.
    Now also requires agreement to privacy agreement
    """

    error_messages = {
        **customSetPasswordForm.error_messages,
        "otp_incorrect": _(
            "Your OTP was entered incorrectly or has expired. Please enter it again or request another."
        ),
        "otp_expired": _("Your OTP has expired. Please request another."),
    }

    otpass = forms.CharField(
        label=_("OTP Verification Code"),
        strip=False,  # keep whitespace
        widget=forms.PasswordInput(attrs={"autofocus": True, "class": "form-control"}),
    )

    field_order = [
        "otpass",
        "new_password1",
        "new_password2",
    ]

    def clean_otpass(self):
        otpass = self.cleaned_data.get("otpass")
        old_otp = OneTimePasswords.objects.filter(user=self.user)
        if old_otp:
            if check_expired(old_otp.first().valid_at):
                raise ValidationError(
                    self.error_messages["otp_expired"],
                    code="otp_expired",
                )
            if not check_password(otpass, old_otp.first().password):
                raise ValidationError(
                    self.error_messages["otp_incorrect"],
                    code="otp_incorrect",
                )
        return otpass


def check_expired(otp):
    now = datetime.datetime.now()
    now = now.replace(tzinfo=datetime.timezone.utc)
    if now > otp + datetime.timedelta(minutes=10):
        return True
    return False
