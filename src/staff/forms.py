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


class StaffUserSearchForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), required=False)
    user_type = forms.MultipleChoiceField(choices=USER_TYPE_CHOICES, widget=forms.SelectMultiple(attrs={"class": "form-control form-select"}), required=False)
    active = forms.BooleanField(label="Only Active Users", widget=forms.CheckboxInput(attrs={"class": "checkbox-inline form-check-input"}), required=False)


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


class HRUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "alt_email",
            "first_name",
            "last_name",
            "phone",
            "unixlogin",
            "user_type",
            "is_active",
        ]
        widgets = {
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
