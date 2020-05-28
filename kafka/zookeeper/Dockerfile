FROM zookeeper:3.4

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone && \
    apk del tzdata
