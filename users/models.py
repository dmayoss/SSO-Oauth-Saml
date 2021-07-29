from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    nickname = models.CharField(max_length=64, null=False, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=32, null=False, blank=True)
    department = models.ManyToManyField('Department')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Department(models.Model):
    department = models.CharField(max_length=128, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.department
