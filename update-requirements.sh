#!/bin/sh
poetry update
poetry export \
    --without-hashes \
    --format requirements.txt \
    --output requirements.dev.txt \
    --all-groups
poetry export \
    --without-hashes \
    --format requirements.txt \
    --output requirements.prod.txt \
    --without=dev \
    --with=postgresql \
    --with=mysql \
    --with=uwsgi \
    --with=daphne
poetry export \
    --without-hashes \
    --format requirements.txt \
    --output requirements.txt \
    --without=dev \
    --with=postgresql \
    --with=mysql \
    --without=uwsgi \
    --without=daphne

exit=$?
if [ $exit -ne 0 ]; then
    echo "[CRITICAL] Failed to export requirements with Poetry!" >&2
    exit $exit
fi