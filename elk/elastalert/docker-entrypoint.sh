#!/bin/sh
set -e

wait-for elasticsearch:9200 \
         --timeout=600 \
         -- true

elastalert-create-index

if [ $? -eq 0 ]
then
    exec "$@"
fi
