FROM wurstmeister/kafka:2.11-2.0.0

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone && \
    apk del tzdata

RUN wget -O /usr/local/bin/wait-for \
         https://raw.githubusercontent.com/eficode/wait-for/master/wait-for \
    && chmod +x /usr/local/bin/wait-for

COPY server.properties ${KAFKA_HOME}/config/server.properties
COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["start-kafka.sh"]
