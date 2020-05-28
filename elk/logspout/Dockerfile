# uses ONBUILD instructions described here:
# https://github.com/gliderlabs/logspout/tree/master/custom

FROM gliderlabs/logspout:master
ENV SYSLOG_FORMAT rfc3164

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone && \
    apk del tzdata

RUN wget -O /usr/local/bin/wait-for \
         https://raw.githubusercontent.com/eficode/wait-for/master/wait-for \
    && chmod +x /usr/local/bin/wait-for

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/bin/logspout"]
