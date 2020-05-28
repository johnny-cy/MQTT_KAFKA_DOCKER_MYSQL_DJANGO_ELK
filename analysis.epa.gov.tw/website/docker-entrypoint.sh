#!/bin/sh
set -e

echo "Apply database migrations"
python3 manage.py migrate
echo ""

if [ ${RELEASE} == "1" ]
then
    echo "Run collectstatic"
    python3 manage.py collectstatic -c --no-input
    echo ""
fi

wait-for mysql:3306 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    exec "$@"
fi
