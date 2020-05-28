FROM cameo/elastalert:latest

WORKDIR /workspace

COPY . /workspace

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "-m", "elastalert.elastalert", "--rule", "api_monitoring.yaml"]
