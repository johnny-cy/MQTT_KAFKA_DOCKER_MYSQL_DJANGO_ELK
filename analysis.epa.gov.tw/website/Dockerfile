FROM cameo/django:latest

WORKDIR /workspace

COPY . .

VOLUME ["/workspace/static"]

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]
