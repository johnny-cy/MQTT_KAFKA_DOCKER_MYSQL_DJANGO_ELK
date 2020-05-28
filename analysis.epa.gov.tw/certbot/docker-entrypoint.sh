#!/bin/sh

DOMAIN="analysis.cameo.tw"
CERT_FOLDER="/etc/letsencrypt/live/${DOMAIN}"

if [ ! -f ${CERT_FOLDER}/fullchain.pem ]
then
    mkdir -p ${CERT_FOLDER}
    cp /workspace/fullchain.pem ${CERT_FOLDER}/
fi

if [ ! -f ${CERT_FOLDER}/privkey.pem ]
then
    mkdir -p ${CERT_FOLDER}
    cp /workspace/privkey.pem ${CERT_FOLDER}/
fi

if [ ! -f ${CERT_FOLDER}/chain.pem ]
then
    mkdir -p ${CERT_FOLDER}
    cp /workspace/chain.pem ${CERT_FOLDER}/
fi

# TODO: restart nginx

wait-for nginx:80 \
         nginx:443 \
         --timeout=600 \
         -- true

if [ $? -eq 0 ]
then
    exec certbot $@
fi
