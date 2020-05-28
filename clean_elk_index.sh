#!/bin/sh

echo "==================== start clean ELK indices =========================="

#logs=$(find /var/lib/docker/containers/ -name *-json.log)
indices=$(curl 'localhost:9200/_cat/indices?v' | awk '{print $3}' | grep 2019)

for index in $indices
        do
                echo "clean index : $index"
                curl -XDELETE "localhost:9200/$index"
        done


echo "==================== end clean ELK indices   =========================="
