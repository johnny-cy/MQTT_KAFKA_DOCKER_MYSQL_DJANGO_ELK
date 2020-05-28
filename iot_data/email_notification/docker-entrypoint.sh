#!/bin/sh
set -e

wait-for kafka:9092 \
         mysql:3306 \
         django:8000 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    exec "$@"
fi
