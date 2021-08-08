from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy, reverse

from users.models import CustomUser, UserKeys
from users.forms import NewUserKeyForm, UserEditForm


class UserEditProfileView(UpdateView):
    model = CustomUser
    fields = [
        'first_name', 'last_name', 'nickname', 'phone',
        'unixname', 'homedir', 'shell',
        ]
    success_url = reverse_lazy('home')
    template_name = 'users/edit_user.html'


class UserEditView(UpdateView):
    model = CustomUser
    form_class = UserEditForm
    template_name = 'home.html'

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(CustomUser, pk=self.kwargs['pk'])
        if obj.pk != self.request.user.id:
            raise PermissionDenied()
        else:
            return obj

    def get_success_url(self, *args, **kwargs):
        return reverse('home')



class UserKeysListView(ListView):
    model = UserKeys

    def get_queryset(self):
        return UserKeys.objects.filter(user=self.request.user)


class UserKeysNewView(CreateView):
    model = UserKeys
    success_url = reverse_lazy("user-keys-list")
    template_name = 'edit_form.html'
    form_class = NewUserKeyForm

    # any new form through this view == your own
    def form_valid(self, form):
        userkeys = form.save(commit=False)
        userkeys.user = CustomUser.objects.get(id=self.request.user.id)
        userkeys.save()
        return super(UserKeysNewView, self).form_valid(form)

    def get_object(self, *args, **kwargs):
        user_key = get_object_or_404(UserKeys, pk=self.kwargs['pk'])
        return user_key

    def get_success_url(self, *args, **kwargs):
        return reverse("user-keys-list")


class UserKeysEditView(UpdateView):
    model = UserKeys
    fields = ['key_data', 'active']
    template_name = 'edit_form.html'

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(UserKeys, pk=self.kwargs['pk'])
        if obj.user_id != self.request.user.id:
            raise PermissionDenied()
        else:
            return obj

    def get_success_url(self, *args, **kwargs):
        return reverse("user-keys-list")


class UserKeysDeleteView(DeleteView):
    model = UserKeys
    fields = ['id']

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(UserKeys, pk=self.kwargs['pk'])
        return obj

    def get_success_url(self, *args, **kwargs):
        return reverse("user-keys-list")


class UserKeysActView(UpdateView):
    model = UserKeys
    fields = ['id']

    def form_valid(self, form):
        userkeys = form.save(commit=False)
        # flip active toggle
        if userkeys.active == True:
            userkeys.active = False
        else:
            userkeys.active = True
        userkeys.save()
        return super(UserKeysActView, self).form_valid(form)

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(UserKeys, pk=self.kwargs['pk'])
        if obj.user_id != self.request.user.id:
            raise PermissionDenied()
        else:
            return obj

    def get_success_url(self, *args, **kwargs):
        return reverse("user-keys-list")
