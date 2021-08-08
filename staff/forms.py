from django import forms
from users.models import CustomUser


class StaffUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'nickname', 'phone', 'unixgroups',
            'unixname', 'homedir', 'shell', 'departments', 'unixlogin',
            ]
