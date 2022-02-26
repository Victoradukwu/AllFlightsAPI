#!/bin/bash
# Exit any executing pipeline
set -e

if [ "$1" = "manage" ]; then
    shift 1
    exec python manage.py "$@"
else
    python manage.py migrate
    python manage.py collectstatic --noinput

    # Log files for stdout
    mkdir -p /srv/logs/
    touch /srv/logs/gunicorn.log
    touch /srv/logs/access.log
    tail -n 0 -f /srv/logs/*.log &

    # Start Gunicorn processes
    echo Starting Gunicorn

    exec gunicorn RecipeHubAPI.wsgi \
        --bind 0.0.0.0:8000 \
        --chdir /usr/src/app \
        --workers 1 \
        --reload \
        --log-level=info \
        --log-file=/srv/logs/gunicorn.log \
        --access-logfile=/srv/logs/access.log
fi
