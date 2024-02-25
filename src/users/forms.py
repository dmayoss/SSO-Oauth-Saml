from captcha.fields import CaptchaField
from django import forms
# from django.core.exceptions import ValidationError

from sso.helper import (
    FORM_ACTION_CHOICES,
    RESET_METHOD_CHOICES,
    ROLES_CHOICES,
    USER_APPLICATION_CHOICES,
    USER_TYPE_CHOICES,
)
from users.models import AppPasswords, CustomUser, Departments, UserRoleMap, UserVacations


class UserNewForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "alt_email",
            "first_name",
            "last_name",
            "phone",
            "unixlogin",
            "user_type",
            "is_active",
        ]
        widgets = {
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "alt_email": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "user_type": forms.Select(
                choices=USER_TYPE_CHOICES, attrs={"class": "form-control form-select"}
            ),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "unixlogin": forms.CheckboxInput(
                attrs={"class": "checkbox-inline form-check-input"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "checkbox-inline form-check-input"}
            ),
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["alt_email", "ooo_message"]
        widgets = {
            "alt_email": forms.TextInput(attrs={"class": "form-control"}),
            "ooo_message": forms.Textarea(attrs={"class": "form-control"}),
        }


class UserRoleMapForm(forms.ModelForm):
    class Meta:
        model = UserRoleMap
        fields = ["department", "user", "role"]
        widgets = {
            "department": forms.Select(attrs={"class": "form-select form-control"}),
            "user": forms.Select(attrs={"class": "form-select form-control"}),
            "role": forms.Select(
                choices=ROLES_CHOICES, attrs={"class": "form-select form-control"}
            ),
        }


class UserRoleMapEditForm(forms.Form):
    role = forms.ChoiceField(
        choices=ROLES_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-control"}),
    )


class DepartmentEditForm(forms.ModelForm):
    class Meta:
        model = Departments
        fields = ["department", "description"]
        widgets = {
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }


class UserVacationForm(forms.ModelForm):
    class Meta:
        model = UserVacations
        fields = ["start_date", "end_date", "vacation_type", "vacation_message"]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', "class": "form-control"}),
            'end_date': forms.DateInput(attrs={'type': 'date', "class": "form-control"}),
            "vacation_message": forms.Textarea(attrs={"class": "form-control"}),
            "vacation_type": forms.Select(attrs={"class": "form-select form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date > end_date:
            msg = "Start Date cannot be greater than End Date."
            self.add_error('start_date', msg)
            self.add_error('end_date', msg)


class DepartmentMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        widget=forms.Select(attrs={"class": "form-select form-control"}),
    )
    action = forms.ChoiceField(
        choices=FORM_ACTION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-control"}),
    )


class userResetMethodForm(forms.Form):
    method = forms.ChoiceField(
        choices=RESET_METHOD_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-control"}),
    )


class UserAppPassEditForm(forms.Form):
    name = forms.CharField(
        label="App. Name",
        max_length=64,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    application = forms.ChoiceField(
        label="New Application",
        choices=USER_APPLICATION_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-control"}),
    )


# don't allow SMS on here to prevent rando's attempting to spam SMS's
class customUserResetPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    captcha = CaptchaField()


class PrivacyAgreementForm(forms.Form):
    agreement = forms.BooleanField(
        label="Accept Agreement",
        widget=forms.RadioSelect(attrs={"class": "form-control"}),
    )
