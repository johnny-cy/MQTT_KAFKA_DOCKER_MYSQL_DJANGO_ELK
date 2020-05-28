#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import epa.logging

from main import main_func
from coordinator import Coordinator
from etl_functions import ETLMixin


logger = epa.logging.get_logger("mqtt_etl")


class MQTTETLer(Coordinator, ETLMixin):

    def post_read(self, data):
        yield from self.etl_value(data)


def main():
    main_func(MQTTETLer,
              process_name="mqtt_etl",
              description="MQTT ETL"
              )


if __name__ == "__main__":
    main()

