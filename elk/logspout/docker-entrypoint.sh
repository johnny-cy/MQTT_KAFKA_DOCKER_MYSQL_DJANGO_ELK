#!/bin/sh
set -e

wait-for logstash:5000 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    exec "$@"
fi
