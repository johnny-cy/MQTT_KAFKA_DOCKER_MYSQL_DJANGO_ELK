#!/bin/sh
set -e

wait-for kafka:9092 \
         mysql:3306 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    time_20_minutes_ago=$(date +"%Y-%m-%d %H:%M:%S" -d@"$(( `date +%s`-1200))")
    exec python3 data_fusion.py -c taichung -d "${time_20_minutes_ago}"
fi
