FROM cameo/epa-python-uwsgi:latest

WORKDIR /workspace

RUN pip3 --no-cache-dir install \
        connexion==1.5.2 \
        Flask==1.0.2

COPY . .

EXPOSE 8002
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
