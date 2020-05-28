# https://github.com/elastic/logstash-docker
FROM docker.elastic.co/logstash/logstash:6.4.0

USER root
RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone
USER logstash

COPY config/* /usr/share/logstash/config/
COPY pipeline /usr/share/logstash/pipeline
