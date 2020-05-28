#!/bin/sh
set -e

wait-for zookeeper:2181 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    exec "$@"
fi
