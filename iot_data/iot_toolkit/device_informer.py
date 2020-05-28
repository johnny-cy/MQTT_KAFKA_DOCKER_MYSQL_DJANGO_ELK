#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get devices information.

This application try to get devices information using RESTful API::

    https://iot.epa.gov.tw/iot/v1/device

"""

import time

from main import main_func
from coordinator import Coordinator
from etl_functions import ETLMixin


class DeviceInformer(Coordinator, ETLMixin):

    def pre_read(self):
        http_handler = self.config.input
        http_handler.post_read_func = self.sleep_one_day

    def post_read(self, data):
        yield from self.etl_value(data)

    def sleep_one_day(self):
        time.sleep(24*60*60)


def main():
    main_func(DeviceInformer,
              process_name="device_informer",
              description="Get device information from iot.epa.gov.tw",
              )


if __name__ == "__main__":
    main()
