from django import forms

from sso.helper import SHELL_CHOICES


class ldapTweakForm(forms.Form):
    value = forms.CharField(label="Value", max_length=128)
    action = forms.CharField(label="Action", max_length=32)


class ldapUserForm(forms.Form):
    # uid/gid set by offset+django pk
    # firstname, lastname, cn set by djangouser
    homedir = forms.CharField(
        label="Home Directory",
        max_length=64,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    username = forms.CharField(
        label="Username",
        max_length=64,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    shell = forms.ChoiceField(
        label="User Shell",
        widget=forms.Select(attrs={"class": "form-select form-control"}),
        choices=SHELL_CHOICES,
    )


class ldapShellForm(forms.Form):
    shell = forms.ChoiceField(
        label="User Shell",
        widget=forms.Select(attrs={"class": "form-select form-control"}),
        choices=SHELL_CHOICES,
    )


class ldapSSHKeyForm(forms.Form):
    sshkey = forms.CharField(
        label="New SSH Key", widget=forms.Textarea(attrs={"class": "form-control"})
    )
