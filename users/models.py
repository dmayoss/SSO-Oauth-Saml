from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelChoiceField
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


class UnixGroups(models.Model):
    group_name = models.CharField(max_length=30, default='group', unique=True)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name_plural = "Unix Groups"


class UnixShells(models.Model):
    shell_name = models.CharField(max_length=30, default='sh')
    shell_path = models.CharField(max_length=30, default='/bin/sh')
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.shell_name

    class Meta:
        verbose_name_plural = "Unix Shells"


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.unixname:
            self.unixname = self.username
        if not self.homedir:
            self.homedir = "/home/{}".format(self.username)
        super().save(*args, **kwargs)

    def SHELLS_LIST():
        shell_list = []

        try:
            shells = UnixShells.objects.all()
            for shell in shells:
                shell_list.append((shell.shell_name, shell.shell_path))
        except:
            pass

        if len(shell_list) == 0:
            shell_list.append(('sh','/bin/sh'))

    nickname = models.CharField(max_length=64, null=False, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    phone = PhoneNumberField()
    departments = models.ManyToManyField('Departments')

    unixname = models.CharField(max_length=64, unique=True)
    unixlogin = models.BooleanField(default=False)
    unixgroups = models.ManyToManyField('UnixGroups')

    homedir = models.CharField(max_length=50, null=False, blank=True, default='')
    shell = models.CharField(max_length=32, default='/bin/sh', choices=SHELLS_LIST())

    @property
    def username(self):
        try:
            return self.email[:self.email.find('@')]
        except:
            return ""

    @property
    def usergroups(self):
        groups = list()
        try:
            for department in self.departments.all():
                groups.append(department.department)
            return groups
        except:
            return groups

    def __str__(self):
        return self.email


class Departments(models.Model):
    department = models.CharField(max_length=128, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.department

    class Meta:
        verbose_name_plural = "Departments"


class UserKeys(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    key_data = models.TextField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "User Keys"

    def __str__(self):
        return "{} {}".format(self.user, self.created)
