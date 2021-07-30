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
Install these via pip

- django (ymmv on whatever version, I'm just using latest)
- djangosaml2idp
- DB packages
  - pymysql (for example, for mysql/mariadb)
  - db-sqlite3

And that's about it.

# Django Setup
run migrate
`python ./manage.py migrate`

create superuser (follow prompts)
`python ./manage.py createsuperuser`

run server
`python ./manage.py runserver 0:8000`
