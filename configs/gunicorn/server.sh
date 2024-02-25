#!/bin/sh

FULLPATH=$(realpath "${0}")
BASEPATH=$(dirname "${FULLPATH}")

cd $BASEPATH/src
gunicorn
