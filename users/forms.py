from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser, UserKeys


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=128, help_text='Enter a valid email address')

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2',]


class NewUserKeyForm(forms.ModelForm):
    class Meta:
        model = UserKeys
        exclude = ['user',]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'nickname', 'phone', 'shell',
            ]
