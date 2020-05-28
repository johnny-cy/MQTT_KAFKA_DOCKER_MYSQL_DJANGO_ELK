FROM cameo/epa-python:latest

WORKDIR /workspace
ENV PATH="/workspace:${PATH}"

RUN pip3 --no-cache-dir install \
        PyYAML==3.13 \
        requests==2.19.1 \
        elasticsearch==6.3.1 \
        paho-mqtt==1.4.0

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]
