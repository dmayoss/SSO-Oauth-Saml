"""
Django settings for sso project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!dji1wg5n9e7ngwp_kkag(q*l3@mm!xlm)tp04-q9a&sm+w)ym'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '*',
    ]

# silence this warning, for django user sessions
SILENCED_SYSTEM_CHECKS = ["admin.E410",]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'djangosaml2idp',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    'user_sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 2FA / OTP x6
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'otp_yubikey',  # apparently needed even if not used. Joy.
    'phonenumber_field',  # have it, may as well use it.
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 2FA / OTP
    'django_otp.middleware.OTPMiddleware',
]

# both sessions changes above, and this, are for django-user-sessions
SESSION_ENGINE = 'user_sessions.backends.db'

ROOT_URLCONF = 'sso.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates')),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sso.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': str(BASE_DIR.joinpath('db.sqlite3')),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssomaster',
        'USER': 'ssomaster',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'sso.auth.EmailBackend',
    ]

LOGIN_URL = 'two_factor:login'
# LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'

# this one is optional
LOGIN_REDIRECT_URL = 'home'
# LOGIN_REDIRECT_URL = 'two_factor:profile'

LOGOUT_REDIRECT_URL = 'home'

# fix me for emails to actually go out
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))

# this is needed for emails to be usernames
AUTH_USER_MODEL = "users.CustomUser"

# SAML stuff below
import saml2
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary

BASE_URL = 'http://localhost:8000/idp'  # change this

SAML_IDP_CONFIG = {
    'debug' : DEBUG,
    'xmlsec_binary': get_xmlsec_binary(['/usr/local/bin/xmlsec1', '/usr/bin', 'usr/local/bin']),
    'entityid': '%s/metadata' % BASE_URL,
    'description': 'Easy IdP',
    'service': {
        'idp': {
            'name': 'Easy IdP',
            'endpoints': {
                'single_sign_on_service': [
                    # maybe should not have the following?
                    ('%s/sso/post/' % BASE_URL, saml2.BINDING_HTTP_POST),
                    ('%s/sso/redirect/' % BASE_URL, saml2.BINDING_HTTP_REDIRECT),
                ],
                "single_logout_service": [
                    # maybe should not have the following?
                    ("%s/slo/post/" % BASE_URL, saml2.BINDING_HTTP_POST),
                    ("%s/slo/redirect/"  % BASE_URL, saml2.BINDING_HTTP_REDIRECT)
                ],
            },
            'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED],
            'sign_response': True,
            'sign_assertion': True,
            'want_authn_requests_signed': True,
        },
    },
    # Signing
    'key_file': str(BASE_DIR.joinpath('certificates/private.key')),
    'cert_file': str(BASE_DIR.joinpath('certificates/public.cert')),
    # Encryption
    'encryption_keypairs': [{
        'key_file': str(BASE_DIR.joinpath('certificates/private.key')),
        'cert_file': str(BASE_DIR.joinpath('certificates/public.cert')),
    }],
    'valid_for': 365 * 24,
}

SAML_AUTHN_SIGN_ALG = saml2.xmldsig.SIG_RSA_SHA256
SAML_AUTHN_DIGEST_ALG = saml2.xmldsig.DIGEST_SHA256

# not sure if I need the following, or if it should be 0
SAML_IDP_FALLBACK_EXPIRATION_DAYS = 30

# this is probably only for SP
SAML_IDP_SP_FIELD_DEFAULT_PROCESSOR = 'djangosaml2idp.processors.BaseProcessor'
SAML_IDP_SP_FIELD_DEFAULT_ATTRIBUTE_MAPPING = {
    "username": "username",  # this is just the email before @
    "usergroups": "usergroups",  # this will need tweaks, I'm sure
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
    "is_staff": "is_staff",
    "is_superuser": "is_superuser"
    }

# 2FA malarkey
TWO_FACTOR_PATCH_ADMIN = True

# TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.twilio.gateway.Twilio'
# TWO_FACTOR_CALL_GATEWAY = 'two_factor.gateways.fake.Fake'
TWO_FACTOR_CALL_GATEWAY = None

TWO_FACTOR_SMS_GATEWAY = None

TWO_FACTOR_TOTP_DIGITS = 6  # default is 6
TWO_FACTOR_LOGIN_TIMEOUT = 600  # default is 600

PHONENUMBER_DEFAULT_REGION = None

TWO_FACTOR_REMEMBER_COOKIE_AGE = 36500  # default is 0, not active

# phonenumber stuff (using phonenumberslite)
# PHONENUMBER_DB_FORMAT = 'E164', 'INTERNATIONAL', 'NATIONAL' or 'RFC3966'
PHONENUMBER_DB_FORMAT = 'E164'
