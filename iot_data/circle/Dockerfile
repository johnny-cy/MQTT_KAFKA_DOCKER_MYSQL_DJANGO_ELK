FROM cameo/circle:latest
#FROM cameo/epa-python:latest

WORKDIR /workspace

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "circle.py", "-c"]
