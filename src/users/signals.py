from logging import getLogger

# logger = getLogger(__name__)
logger = getLogger("sso")
# logger.setLevel(logging.INFO)

# from django.core.signals import request_finished
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.db.models.signals import (
    post_delete,
    post_init,
    post_save,
    pre_init,
    pre_save,
)
from django.dispatch import receiver
from django.utils import timezone
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from two_factor.signals import user_verified

from sso.helper import get_client_ip
from users.models import AppPasswords, CustomUser, Departments, UserRoleMap

"""
Admin things - generally should never/rarely happen
"""


@receiver(post_delete, sender=CustomUser)
def delete_user(sender, instance, **kwargs):
    logger.info("[ADMIN]: USER ACCOUNT FOR {} WAS DELETED".format(instance))


"""
User Login/Logout
"""


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    logger.info("user {} logged in from {}".format(user, ip))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    logger.info("user {} logged out from {}".format(user, ip))


@receiver(user_login_failed)
def user_login_failed_callback(sender, request, credentials, **kwargs):
    ip = get_client_ip(request)
    # credentials uses 'username' field
    logger.info(
        "login failed for {} from {} in {}".format(
            credentials.get("username", None), ip, sender
        )
    )


"""
MFA Models Create (MFA enable/disable)
"""


def totp_device_create(sender, instance, created, **kwargs):
    if created:
        logger.info("user {} created a TOTP Device".format(instance.user))
    else:
        logger.info(
            "user {} instanced a TOTP Device (successful password?)".format(
                instance.user
            )
        )


def totp_device_delete(sender, instance, **kwargs):
    logger.info("user {} deleted a TOTP Device".format(instance.user))


def static_device_create(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "user {} created a Static TOTP Device (for backup codes)".format(
                instance.user
            )
        )
    else:
        logger.info(
            "user {} instanced a Static Device (successful password?)".format(
                instance.user
            )
        )


def static_device_delete(sender, instance, **kwargs):
    logger.info(
        "user {} deleted a Static Device (for backup codes)".format(instance.user)
    )


def static_token_create(sender, instance, **kwargs):
    logger.info("user {} created a Backup Code (2FA)".format(instance.device.user))


def static_token_delete(sender, instance, **kwargs):
    logger.info(
        "user {} used (i.e. successful login via) or deleted a Backup Code (2FA)".format(
            instance.device.user
        )
    )


post_save.connect(totp_device_create, sender=TOTPDevice)
post_delete.connect(totp_device_delete, sender=TOTPDevice)
post_save.connect(static_device_create, sender=StaticDevice)
post_delete.connect(static_device_delete, sender=StaticDevice)
post_save.connect(static_token_create, sender=StaticToken)
post_delete.connect(static_token_delete, sender=StaticToken)


"""
User Account
"""


@receiver(pre_save, sender=CustomUser)
def user_updated(sender, **kwargs):
    user = kwargs.get("instance", None)

    if user:
        try:
            old_user = CustomUser.objects.get(pk=user.pk)
        except CustomUser.DoesNotExist:
            logger.info("user account being created for {}".format(user))
        else:
            if user.unixlogin != old_user.unixlogin:
                logger.info(
                    "unix login set {} for user {}".format(user.unixlogin, user)
                )

            if user.is_active != old_user.is_active:
                logger.info(
                    "account active set {} for user {}".format(user.is_active, user)
                )

            if user.alt_email != old_user.alt_email:
                logger.info("user {} changed their alternate email".format(user))

            if user.password != old_user.password:
                logger.info("user {} changed their password".format(user))


"""
MFA
"""


@receiver(user_verified)
def user_mfa_verified(sender, request, user, device, **kwargs):
    ip = get_client_ip(request)
    logger.info(
        "user {} was MFA verified by device {} from {} by {}".format(
            user, device, ip, sender
        )
    )


"""
Application Passwords
"""


@receiver(post_save, sender=AppPasswords)
def update_app_password(sender, instance, created, **kwargs):
    # ip = get_client_ip(request)
    if created:
        logger.info(
            "user {} created an app password for {}".format(
                instance.user, instance.application
            )
        )
    else:
        logger.info(
            "user {} updated their app password for {}".format(
                instance.user, instance.application
            )
        )


@receiver(post_delete, sender=AppPasswords)
def delete_app_password(sender, instance, **kwargs):
    # ip = get_client_ip(request)
    logger.info(
        "user {} deleted their app password for {}".format(
            instance.user, instance.application
        )
    )


"""
User Roles
"""


@receiver(post_save, sender=UserRoleMap)
def update_user_roles(sender, instance, created, **kwargs):
    # ip = get_client_ip(request)
    if created:
        logger.info(
            "a user role for {} in department {} was created".format(
                instance.user, instance.department
            )
        )
    else:
        logger.info(
            "a user role for {} in department {} was updated".format(
                instance.user, instance.department
            )
        )


@receiver(post_delete, sender=UserRoleMap)
def delete_user_roles(sender, instance, **kwargs):
    logger.info(
        "a user role for {} in {} was deleted".format(
            instance.user, instance.department
        )
    )


"""
Departments
"""


@receiver(post_save, sender=Departments)
def update_departments(sender, instance, created, **kwargs):
    # ip = get_client_ip(request)
    if created:
        logger.info("department {} was created".format(instance.department))
    else:
        logger.info("department {} was updated".format(instance.department))


@receiver(post_delete, sender=Departments)
def delete_departments(sender, instance, **kwargs):
    logger.info("departent {} was deleted".format(instance))
