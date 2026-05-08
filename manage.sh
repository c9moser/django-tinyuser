#!/bin/sh

poetry run python manage.py "$@"
exit $?
