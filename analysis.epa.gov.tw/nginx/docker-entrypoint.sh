#!/bin/sh
set -e

wait-for django:8000 \
         api_public:8001 \
         api_internal:8002 \
         adminer:8080 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    exec "$@"
fi
