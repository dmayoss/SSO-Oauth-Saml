import base64
import hashlib
import requests

from logging import getLogger

logger = getLogger("sso")

# this block is for the password reset view
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from sso.secrets import (
    INFOBIP_FROM,
    INFOBIP_PASS,
    INFOBIP_USER,
    SITE_ADMIN_EMAIL,
    SITE_DOMAIN,
    SITE_PROTOCOL,
)

from sso.tokens import account_activation_token


# Don't know if these will ever be used, are there any other types?
VACATION_CHOICES = [
    ("PERSONAL", "Sabbatical / Other"),
    ("SICK", "Sick Leave"),
    ("PTO", "Vacation"),
]

# These choices are hard coded as they don't often change
SHELL_CHOICES = [
    ("/bin/sh", "sh"),
    ("/usr/local/bin/bash", "bash"),
    # ('/usr/local/bin/fish', 'fish'),
]

# future apps
USER_APPLICATION_CHOICES = [
    ("EMAIL", "Email"),
    # ('VPN', 'VPN'),
    # ('SAML', 'SAML'),
    # ('GITLAB', 'Gitlab'),
]

# Department Roles
ROLES_CHOICES = [
    ("ADMIN", "Admin"),
    ("USER", "User"),
]

# User types, e.g. HR can add ADMIN users to Departments
USER_TYPE_CHOICES = [
    ("USER", "Normal User"),
    ("HR", "HR User"),
    ("HOSTING", "Hosting User"),
    ("RETIRED", "Retired User"),
    ("INTERNAL", "Internal (non-employee) User"),
]

FORM_ACTION_CHOICES = [
    ("ADD", "Add"),
    ("DEL", "Remove"),
]

RESET_METHOD_CHOICES = [
    ("EMAIL", "Email + OTP"),
    ("ALTEMAIL", "Alternate Email + OTP"),
    ("SHOWEMAIL", "Email, Display OTP"),
    ("SHOWALT", "Alternate Email, Display OTP"),
]


def app_check_pass(password, app_pass_set):
    """
    checks the given password against the given app password entries
    """

    # this should never happen, but I might cheap out and let this function do it in future
    if app_pass_set.count() == 0:
        return False

    for app_pass in app_pass_set:
        try:
            result = check_password(password)
        except:
            # something goes boom, we fail
            return False
        else:
            # if one matches, we gucci
            if result == True:
                return True

    return False


# making sure ldapuser has all three wanted objectClasses
# there's probably a better way to do this, but these three are all I need
def check_ldapuser_objectclasses(ldapuser):
    # when just creating, there won't be an objectclass
    # so this is either catch22 or we need to save before we get here
    if not ldapuser.objectclass:
        result = {
            "content": "LDAP user {} updated".format(ldapuser),
            "error": False,
        }
        return ldapuser, result

    changed = False

    if "posixAccount" not in ldapuser.objectclass:
        ldapuser.objectclass.append("posixAccount")
        changed = True

    if "inetOrgPerson" not in ldapuser.objectclass:
        ldapuser.objectclass.append("inetOrgPerson")
        changed = True

    if "ldapPublicKey" not in ldapuser.objectclass:
        ldapuser.objectclass.append("ldapPublicKey")
        changed = True

    if changed == True:
        try:
            ldapuser.save()
        except Exception as e:
            result = {
                "content": "error saving LDAP user : {}".format(e),
                "error": True,
            }
        else:
            result = {
                "content": "LDAP User {} Object Classes updated".format(
                    ldapuser.username
                ),
                "error": False,
            }
    else:
        # if nothing is done, we don't need to know.
        result = {
            "content": None,
            "error": False,
        }

    return ldapuser, result


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def generate_message(user, method):
    if method == "EMAIL":
        msg_template = "accounts/password_reset_email.txt"
    elif method == "SMS":
        msg_template = "accounts/password_reset_sms.txt"

    c = {
        "domain": SITE_DOMAIN,
        "protocol": SITE_PROTOCOL,
        "user": user,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    }

    return render_to_string(msg_template, c)


def generate_otp_message(otpass):
    msg_template = "accounts/password_reset_otp.txt"

    c = {
        "otpass": otpass,
    }

    return render_to_string(msg_template, c)


def send_reset_email_with_otp(user, otpass, altEmail=False, displayOTP=False):
    """
    Sends both an email and an SMS.
    Email has the link
    SMS has the verification code (OTP)
    """

    email_message = generate_message(user, "EMAIL")

    send_reset_email(user, email_message, altEmail)

    if altEmail:
        to_email = user.alt_email
    else:
        to_email = user.email

    if displayOTP:
        return "Reset link has been sent to {}, OTP is: {}".format(to_email, otpass)
    else:
        sms_message = generate_otp_message(otpass)
        send_reset_sms_json(user, sms_message)
        return "email/sms-otp has been sent for user {} to {}/{}".format(
            user, to_email, user.phone
        )


def send_reset_email(user, email_message=None, altEmail=False):
    email_from = SITE_ADMIN_EMAIL
    subject = "Password Reset Requested"

    if not email_message:
        email_message = generate_message(user, "EMAIL")

    if altEmail:
        email_to = user.alt_email
    else:
        email_to = user.email

    try:
        send_mail(subject, email_message, email_from, [email_to], fail_silently=False)
        logger.info("Sending Password Reset Email to {} for {}".format(email_to, user))
    except Exception as e:
        result = {
            "error": True,
            "content": "{}".format(e),
        }
    else:
        result = {
            "error": False,
            "content": "Success",
        }

    return result


def send_reset_sms_json(user, sms_message):
    infobip_url = "http://api.infobip.com/api/v3/sendsms/json"
    recipient = str(user.phone)

    json_payload = {
        "authentication": {
            "username": INFOBIP_USER,
            "password": INFOBIP_PASS,
        },
        "messages": [
            {
                "sender": INFOBIP_FROM,
                "text": sms_message,
                "recipients": [{"gsm": recipient}],
            }
        ],
    }

    return requests.post(infobip_url, json=json_payload)


def send_reset_sms(user):
    sms_message = generate_message(user, "SMS")
    return send_reset_sms_json(user, sms_message)


"""
user.user_type can be: USER, HR, HOSTING
will check also user.is_staff and user.is_superuser

effectively:
  - HOSTING makes you ALSO HR
  - is_superuser makes you is_staff

use with decorator user_passes_test (func = user_is_hr)

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(func, [login_url='/login/'])
def my_view(request)
"""


def user_is_hosting(user):
    if not user.is_authenticated:
        return False
    else:
        return user.user_type == "HOSTING"


def user_is_hr(user):
    if not user.is_authenticated:
        return False
    else:
        return user.user_type == "HR" or user_is_hosting(user)


def user_is_staff(user):
    if not user.is_authenticated:
        return False
    else:
        return user.is_superuser or user.is_staff


def test_is_staff_or_ldapuser(user, ldapuser):
    if not user.is_authenticated:
        return False

    if user.username != ldapuser.username:
        return user_is_hr(user)
    else:
        return True


def generate_sshkey_fingerprint(sshkey):
    """
    This will:
    - strip unwanted spaces
    - split on space inside the string, e.g. "ssh-rsa [key] comment"
    - hash the key
    - prettify the fingerprint into xx:xx:xx format
    """
    try:
        # split and prettify
        splitkey = sshkey.strip().split()
        keytype = splitkey[0]
        keystring = splitkey[1]
        keycomment = splitkey[2]

        # encode/hash
        key = base64.b64decode(keystring.encode("ascii"))  # or utf-8 ?
        fp_plain = hashlib.md5(key).hexdigest()
        keyfp = ":".join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))
    except Exception as e:
        result = {
            "keytype": None,
            "keyfp": None,
            "keycomment": None,
            "error": "{}".format(e),
        }
    else:
        result = {
            "keytype": keytype,
            "keyfp": keyfp,
            "keycomment": keycomment,
            "error": None,
        }

    return result
