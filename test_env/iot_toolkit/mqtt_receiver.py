#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from main import main_func
from coordinator import Coordinator


class MQTTReceiver(Coordinator):
    pass


def main():
    main_func(MQTTReceiver,
              process_name="mqtt_receiver",
              description="Receive MQTT data, and send them to Kafka",
              )


if __name__ == "__main__":
    main()

