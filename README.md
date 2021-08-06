# userdb
my (very simple) user database app in django, uses custom user model

# setup
My target for various reasons is FreeBSD, so ymmv but this is DJango, so it'll work almost everywhere that does.

## system packages
You need the equivalent of:

- python38 (ymmv on other versions)
- virtualenv (you can do without)
- pip
- xmlsec1
- rust
- nginx (or your http server of choice)
- gunicorn (or uwsgi or similar)
  - it's actually better to install this via pip if using a virtualenv
- a DB backend of some sort
  - mariadb
  - mysql
  - postgres
  - sqlite3 (db-sqlite3 via pip)
- DB interface modules (Depending on need/compatibility)
  - py38-postgresql
  - py38-sqlite3
  - py38-pymysql
  - py38-mysqlclient
  - py38-mysql-connector-python


## python packages
It's recommended to use the `requirements.txt` file via:

`pip install -r requirements.txt`

but you can also just install these via pip:

- django (ymmv on whatever version, I'm just using latest)
- djangosaml2idp
- DB packages
  - pymysql (for example, for mysql/mariadb)
  - db-sqlite3
- django-two-factor-auth[phonenumberslite]
  - alternatively, django-two-factor-auth[phonenumbers]
- django-user-sessions
- django-yubi-otp

And that's about it.

**Note**: You may need more packages if my list for things like database access isn't what it should be.

# Django Setup
## make missing directories
You need some SSL certs for SAML to work.
`mkdir certificates`

Oh, and make those certs
`openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout server.key -out server.crt`

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
