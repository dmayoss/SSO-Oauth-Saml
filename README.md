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

## python packages
Install these via pip

- django (ymmv on whatever version, I'm just using latest)
- djangosaml2idp
- DB packages
  - pymysql (mysql/mariadb)
  - db-sqlite3 (sqlite)

And that's about it.

More configuration will follow later.
