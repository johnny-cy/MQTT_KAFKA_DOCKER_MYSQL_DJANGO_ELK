# https://github.com/elastic/elasticsearch-docker
FROM docker.elastic.co/elasticsearch/elasticsearch:6.4.0

RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone

COPY config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
