from django.contrib.auth import get_user_model
from django.db import models
from django.utils.crypto import get_random_string


class OneTimePasswords(models.Model):
    """
    An OTP designed to be used once during initial setup or if TOTP is missing/deactivated
    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    password = models.TextField()
    valid_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_pass(length=12):
        return get_random_string(length=length)

    class Meta:
        verbose_name_plural = "OneTime Passwords"
