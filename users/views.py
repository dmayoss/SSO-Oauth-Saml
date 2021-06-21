from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from users.models import CustomUser
from django.views.generic.edit import CreateView, UpdateView


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class UserEditView(UpdateView):
    model = CustomUser
    fields = ['first_name', 'last_name', 'department', 'phone',]
    success_url = reverse_lazy('home')
    template_name = 'users/edit_user.html'

    def get_object(self, queryset=None):
        return self.request.user
