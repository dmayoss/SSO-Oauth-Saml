# userdb

my (very simple) user database app in django.

## Basics
- custom user model, with email as the django username identifier
  - `username` is now a property which strips the `@domain` from email field
  - this is used for LDAP integration as the `cn`
- provides the following interfaces:
  - `oauth` & fake gitlab for things that support gitlab
  - saml 2.0 idp (via patched uniAuth, see https://uniauth.readthedocs.io/)
  - ldapdb interface because that's how we roll
    - i.e. we USE ldapdb, so there are 2 databases in use


## Environment
My target for various reasons is FreeBSD, so ymmv but this is DJango, so it'll work almost everywhere that does.
This software currently assumes a python virtual environment wil be used, with `pip` to install components.

Use Python 3.9+ and something like gunicorn, with nginx.


## Packages

### System Packages
You will need the equivalent of the following system packages at a minimum:

- python39+ (ymmv on other versions)
- virtualenv & pip (you can do without if you're only install system packages)
- xmlsec1
- nginx (or your http server of choice)
- ldap
- openssl
- a DB backend
  - mariadb or mysql
  - django also supports the following, but I'm not using them:
    - postgres
    - sqlite3

Please note some may be missing.

### Compilers
You may need the following compilers and libraries, depending on how you install software:

- rust
- GCC/clang

### Python Packages
You will need the equivalent of the following python packages.
See `requirements.txt` for actual versions (and use `pip` to install), but the big boys are in general:

- django 3.2 (latest, argon2 version)
  - uniauth for SAML
  - django-two-factor-auth for 2FA
  - django-ldapdb for ldap integration (this will pull in extra ldap packages)
- gunicorn (or uwsgi, or similar)
- mysql-connector-python

## LDAP Server
You will also need an LDAP server for the eventual integration with `sssd`. I have been using OpenLDAP.

I have also been using phpLDAPAdmin to administer OpenLDAP, but managing either of these is more or less out of scope from this Readme file.

The LDAP DB is more or less fully administrable from SSO directly, but an initial setup is required. See schema for details.

## Basic Installation

### Initial System Packages
Using your favourite system package manager (or roll your own), install all necessary system packages.

A comprehensive list should be here, but isn't. Short version was above.

You want to make sure that as much as possible is done via system packages rather than compiling in pip because
you really shouldn't be compiling in the machine you're installing to. Only real downside with `pip` and python.

### Python Virtualenv
Create and activate a Python3.9 VirtualEnv using some command similar to the following:

```
virtualenv -p /usr/local/bin/python3.9 ~/venv
source ~/venv/bin/activate
```

### Python Installation
you'll need to `cd` to where you stored the git checkout, then install the components.

It's recommended to use the `requirements.txt` file via:

```
cd ~/userdb
pip install -r requirements.txt
```

And that's about it.

**Note**: You may need more packages if my list for things like database access isn't what it should be.


# Django Setup

## create SSL Certificates
You need some SSL certs for SAML to work. These should also be used as the nginx certificates, so these instructions will fail.

```
cd ~/userdb
mkdir certificates
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt
```


## check your settings
You'll need to make sure the path to `xmlsec1` is set properly, you'll want to set your secrets properly
and doubtless you'll have different database setups than me. Check all the things.

## run migrate
`python ./manage.py migrate`

## create superuser (follow prompts)
`python ./manage.py createsuperuser`

## run server
`python ./manage.py runserver 0:8000`

**Note**: Of course, you'll want something like `uwsgi` or `gunicorn` when using it properly

# fixing LDAP/PIP installations
Some packages won't build properly inside `pip` without system packages, as for some reason the FreeBSD path for `include` isn't being set properly. To fix this, add the following line to `.profile` (or similar `rc` file for your environment).
```
export CPPFLAGS=-I/usr/local/include
```

# Patch uniauth
Uniauth needs to be patched as it expects an 'Accounts' webapp that doesn't exist where it expects to find it. Some other basic patching has been too.

The required patch file is `.../tools/patches/uniauth-saml2-idp-2.0.1.patch` and needs to be applied to the uniauth package installed with `pip`.

```
cd .../venv/lib/site-packages/uniauth
patch -p0 < /path/to/tools/patches/uniauth-saml2-idp-2.0.1.patch
```

The patch file hasn't been formatted properly, so you'll doubtless have to specify the files it should be patching.

After the files have been patched, SSO should be good to go.