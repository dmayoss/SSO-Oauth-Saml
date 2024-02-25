import re
from logging import getLogger

# logger = getLogger(__name__)
logger = getLogger("sso")
# logger.setLevel(logging.INFO)

from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField

from appdb.models import getLdapGroupMembership, getLdapUserInfo
from sso.helper import ROLES_CHOICES, USER_APPLICATION_CHOICES, USER_TYPE_CHOICES, VACATION_CHOICES

from .managers import CustomUserManager


class PrivacyAgreement(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    agreement = models.BooleanField(default=False, verbose_name="Agreement Accepted")
    verified = models.BooleanField(default=False, verbose_name="Agreement Verified")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Privacy Agreements"

    def __str__(self):
        return "{} {}".format(self.user, self.agreement)


class AppPasswords(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    name = models.CharField(
        max_length=64, null=False, blank=True, verbose_name="Entry Name"
    )
    application = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="Application",
        choices=USER_APPLICATION_CHOICES,
    )
    username = models.CharField(
        max_length=64, null=False, blank=False, verbose_name="Application Username"
    )
    password = models.TextField()
    pvt_crt = models.TextField(blank=True, null=False)
    pvt_key = models.TextField(blank=True, null=False)
    active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Application Passwords"
        unique_together = ["user", "application", "name"]

    @staticmethod
    def generate_pass(length=32):
        return get_random_string(length=length)

    def __str__(self):
        return "{} {}".format(self.user, self.application)


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.alt_email:
            self.alt_email = self.email

        if not self.original_email:
            self.original_email = self.email

        super().save(*args, **kwargs)

    def persistent_ids(self):
        return [i.persistent_id for i in self.persistentid_set.filter(user=self)]

    def persistent_id(self, entityid):
        """returns persistent id related to a recipient (sp) entity id"""
        pid = PersistentId.objects.filter(user=self, recipient_id=entityid).last()
        if pid:
            return pid.persistent_id

    def set_persistent_id(self, recipient_id, persistent_id):
        d = dict(user=self, recipient_id=recipient_id, persistent_id=persistent_id)
        persistent_id = self.persistentid_set.get_or_create(**d)

    def clear_sessions(self):
        try:
            self.session_set.all().delete()
        except Exception as e:
            logger.debug("{}".format(e))

    email = models.EmailField(unique=True, verbose_name="Email Address")
    alt_email = models.EmailField(
        unique=True, verbose_name="Alternate Email Address", null=True, blank=True
    )
    original_email = models.EmailField(
        unique=True, verbose_name="Original Email Address", null=True, blank=True
    )
    unixlogin = models.BooleanField(default=False, verbose_name="Unix Login Enabled")
    user_type = models.CharField(
        choices=USER_TYPE_CHOICES,
        default="USER",
        max_length=16,
        verbose_name="User Type",
        null=False,
        blank=False,
    )
    phone = PhoneNumberField()

    # basic OoO
    is_ooo = models.BooleanField(default=False, verbose_name="Out of Office")
    ooo_message = models.TextField(null=False, blank=True)

    @property
    def uid(self):
        try:
            return re.sub(r"\W+", "", self.email[: self.email.find("@")])
        except:
            return self.email.split("@")[0]

    @property
    def username(self):
        return self.email.split("@")[0]

    @property
    def departments(self):
        groups = list()
        try:
            for rolemap in self.userrolemap_set.all():
                groups.append(rolemap.department.department)
            return groups
        except:
            return groups

    @property
    def on_vacation(self):
        try:
            qs = self.uservacations_set.exclude(end_date__date__lt=timezone.now()).exclude(start_date__date__gt=timezone.now())
            if qs.count() > 0:
                return True
            else:
                return False
        except:
            return False

    @property
    def ldapgroups(self):
        groups = getLdapGroupMembership(self.username)
        return groups

    @property
    def ldapuser(self):
        userinfo = getLdapUserInfo(self.username)
        return userinfo

    def __str__(self):
        return self.email


class Departments(models.Model):
    department = models.CharField(max_length=128, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.department

    class Meta:
        verbose_name_plural = "Departments"


class UserVacations(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    vacation_type = models.CharField(max_length=128, choices=VACATION_CHOICES)
    vacation_message = models.TextField()
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} | {}".format(self.user, self.start_date)

    class Meta:
        verbose_name_plural = "Vacations"


class UserRoleMap(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    department = models.ForeignKey("Departments", on_delete=models.CASCADE)
    role = models.CharField(max_length=128, choices=ROLES_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}: {} - {}".format(self.department, self.user, self.role)

    class Meta:
        verbose_name_plural = "User Departments and Roles"
        unique_together = [
            "user",
            "department",
        ]


class PersistentId(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    persistent_id = models.CharField(
        "SAML Persistent Stored ID", max_length=254, blank=True, null=True
    )
    recipient_id = models.CharField(
        "SAML ServiceProvider entityID", max_length=254, blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Persistent Id"
        verbose_name_plural = "Persistent Id"

    def __str__(self):
        return "{}: {} to {} [{}]".format(
            self.user, self.persistent_id, self.recipient_id, self.created
        )
