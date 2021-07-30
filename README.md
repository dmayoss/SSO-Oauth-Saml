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
- mariadb server (mysql works, postgres will work, you don't need any if you don't want to use a DB)

## python packages
Install these via pip

- django (ymmv on whatever version, I'm just using latest)
- djangosaml2idp
- pymysql (if you're using it)

And that's about it.

More configuration will follow later.
