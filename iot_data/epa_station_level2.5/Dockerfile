FROM cameo/epa-python-sklearn:latest

WORKDIR /workspace

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "cameo_ml.py", "-f", "all"]
