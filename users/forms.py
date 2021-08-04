from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser

# Sign Up Form
class SignUpForm(UserCreationForm):
    # first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    # last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address')

    class Meta:
        model = CustomUser
        fields = [
            'email',
            # 'first_name',
            # 'last_name',
            # 'phone',
            'password1',
            'password2',
            ]
