FROM cameo/email_notification:latest

WORKDIR /workspace

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "email_notification.py"]
