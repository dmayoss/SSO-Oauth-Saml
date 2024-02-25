"""MFA Enforcing Middleware"""

"""
It's not very pretty or tactful, but I don't care.
it checks if user.otp_device is set.
if not, then the user has not used an otp_device to verify themselves.
You'd think we could use user.is_verified but that's not useful
if a user has not got any otp devices, then is_verified isn't set to False/True or even None
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from users.models import CustomUser

MFA_URL_PREFIX_LIST = getattr(settings, "MFA_URL_PREFIX_LIST", {"/idp", "/oauth"})
MFA_ENROLL_PATH = getattr(settings, "MFA_ENROLL_PATH", {"/account/two_factor/"})


class TwoFactorEnforceMiddleware(MiddlewareMixin):
    """
    This middleware checks to see if the user has enrolled in MFA, and if they have not
    then they will always be redirected to the MFA enrollment page.
    """

    def process_request(self, request):
        """Process each request to app to ensure MFA is enrolled"""
        current_path = request.META["PATH_INFO"]

        if request.user.is_authenticated and is_path_protected(current_path):
            if request.user.otp_device == None:
                """
                It would be nice if I could do this with more tact.
                """
                return HttpResponseRedirect("/account/two_factor/")

        return None


def is_path_protected(path):
    """
    returns True if given path is to be protected, otherwise False
    The path is to be protected when it appears on MFA_URL_PREFIX_LIST
    """

    protected = False

    for include_path in MFA_URL_PREFIX_LIST:
        if path.startswith(include_path):
            return True

    return protected
