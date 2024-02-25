import functools
from re import compile

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.functional import SimpleLazyObject

from users.models import PrivacyAgreement

# EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/')), 'tos']
# if hasattr(settings, 'TOS_EXEMPT_URLS'):
#    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class TOSMiddleware:
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware` and
    sets `request.user.is_tos` to True or False based on if there either
    is a matching PrivacyAgreement that is set to True, or not.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user is not None:
            request.user = SimpleLazyObject(
                functools.partial(self._verify_user, request, user)
            )

        return self.get_response(request)

    def _verify_user(self, request, user):
        """
        Sets whether the user has agreed to the ToS or not
        """
        user.tos_agreed = False
        user.tos_verified = False

        if user.is_authenticated:
            agreement, created = PrivacyAgreement.objects.get_or_create(
                user=user, defaults={"agreement": False, "verified": False}
            )

            user.tos_agreed = agreement.agreement
            user.tos_verified = agreement.verified

        return user

    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The ToS middleware\
 requires tos middleware to be installed. Edit your\
 MIDDLEWARE_CLASSES setting to insert\
 'users.middlware.TOSMiddleware'."

        if (request.user.tos_verified == True) and (request.user.tos_agreed == False):
            '''
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect('tos_denied')
            '''
            return HttpResponse('tos')

        return HttpResponse('tos')
    """
