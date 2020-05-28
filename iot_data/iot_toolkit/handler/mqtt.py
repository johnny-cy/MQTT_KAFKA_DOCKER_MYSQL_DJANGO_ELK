#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import queue
import json

import paho.mqtt.client as mqtt
import epa.logging

from . import Handler


logger = epa.logging.get_logger(__name__)
mqtt_logger = epa.logging.get_logger("paho.mqtt")

DEFAULT_HOST = "iot.epa.gov.tw"


class MQTTHandler(Handler):
    handler_id = "mqtt"

    def __init__(self, topics, host=DEFAULT_HOST):
        self.topics = topics
        self.host = host
        self.mqtt_client = None

    def setup_mqtt(self):
        mqtt_client = mqtt.Client()
        mqtt_client.enable_logger(mqtt_logger)
        mqtt_client.username_pw_set(username=self.project.api_key,
                                    password=self.project.api_key)

        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_disconnect = self.on_disconnect
        mqtt_client.on_message = self.on_message
        mqtt_client.on_subscribe = self.on_subscribe
        mqtt_client.on_unsubscribe = self.on_unsubscribe
        mqtt_client.on_publish = self.on_publish

        mqtt_client.connect(self.host, port=1883, keepalive=180)
        logger.info(f"Connecting to MQTT host: {self.host}")

        self.mqtt_client = mqtt_client
        self.queue = queue.Queue(4096)

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT connect, flags = {flags}, rc = {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"MQTT disconnect, rc = {rc}")

    def on_message(self, client, userdata, message):
        try:
            self.queue.put_nowait(message.payload)
        except queue.Full:
            logger.error(f"MQTTHandler's queue is full, drop data.")

    def on_publish(self, client, userdata, mid):
        #logger.info(f"message published: id {mid}")
        pass

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logger.info(f"MQTT subscribe, mid = {mid}, granted_qos = {granted_qos}")

    def on_unsubscribe(self, client, userdata, mid):
        logger.warning(f"MQTT unsubscribe, mid = {mid}")

    def read(self, timeout=3.0):
        self.setup_mqtt()

        topics_with_qos = [(t, 0) for t in self.topics]
        self.mqtt_client.subscribe(topics_with_qos)

        self.mqtt_client.loop_start()
        while True:
            try:
                data = self.queue.get(timeout=timeout)
                yield json.loads(data)
            except queue.Empty:
                logger.debug(f"MQTTHandler's queue is empty, return empty.")
                yield {}
            except json.decoder.JSONDecodeError as e:
                logger.error(f"JSONDecodeError for value: {data}") 

    def write(self, value):
        # FIXME: temporal fix, not good
        if not self.mqtt_client:
            self.setup_mqtt()
            self.mqtt_client.loop_start()

        payload = json.dumps(value)
        for topic in self.topics:
            ret = self.mqtt_client.publish(topic, payload, qos=1)
            ret.wait_for_publish()
            logger.info(f"Message {ret.mid} was sent to topic {topic}: {value}")

    def close(self):
        if self.mqtt_client:
            self.mqtt_client.loop_stop()

