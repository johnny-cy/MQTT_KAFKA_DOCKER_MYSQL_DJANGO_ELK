FROM mariadb:10.3

RUN cp /usr/share/zoneinfo/Asia/Taipei /etc/localtime && \
    echo "Asia/Taipei" >  /etc/timezone

RUN apt-get update \
    && apt-get install -y \
        mariadb-plugin-rocksdb \
    && rm -rf /var/lib/apt/lists/*

COPY cameo.cnf /etc/mysql/conf.d/
COPY docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/
