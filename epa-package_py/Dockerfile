ARG BASE_IMAGE
FROM $BASE_IMAGE:latest

COPY . /workspace
RUN pip3 --no-cache-dir install /workspace \
    && rm -rf /workspace
