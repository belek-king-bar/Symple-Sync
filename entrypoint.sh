#!/bin/sh

python /code/manage.py migrate --noinput

exec "$@"