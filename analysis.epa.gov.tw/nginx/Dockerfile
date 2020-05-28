FROM cameo/nginx:latest

COPY nginx_http.conf /etc/nginx/conf.d/default.conf
COPY htpasswd /etc/nginx/htpasswd
COPY docker-entrypoint.sh .

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
