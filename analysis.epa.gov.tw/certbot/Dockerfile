FROM certbot/certbot:latest

RUN wget -O /usr/local/bin/wait-for \
         https://raw.githubusercontent.com/eficode/wait-for/master/wait-for \
    && chmod +x /usr/local/bin/wait-for

WORKDIR /workspace

COPY docker-entrypoint.sh .
COPY self_signed/* ./

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["certonly", "--webroot", "--email", "yikai@cameo.tw", "--agree-tos", "-w", "/var/www/letsencrypt", "-d", "analysis.cameo.tw"]
