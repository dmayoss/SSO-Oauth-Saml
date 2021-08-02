from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=64, null=False, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=32, null=False, blank=True)
    departments = models.ManyToManyField('Departments')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def username(self):
        try:
            return self.email[:self.email.find('@')]
        except:
            return ""

    @property
    def usergroups(self):
        try:
            groups = list()
            for department in self.departments.all():
                groups.append(department.department)
            return groups
        except:
            return list()


    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Departments(models.Model):
    department = models.CharField(max_length=128, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.department
