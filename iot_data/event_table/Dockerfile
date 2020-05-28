FROM cameo/epa-python:latest

WORKDIR /workspace

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "event_table.py", "-c"]
