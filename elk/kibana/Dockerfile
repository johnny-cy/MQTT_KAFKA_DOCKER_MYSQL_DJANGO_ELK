# https://github.com/elastic/kibana-docker
FROM docker.elastic.co/kibana/kibana:6.4.0

USER root
RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone
USER kibana

COPY config/ /usr/share/kibana/config
