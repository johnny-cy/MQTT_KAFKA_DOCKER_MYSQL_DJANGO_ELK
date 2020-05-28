#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import epa.logging
from epa.utils import get_class_with_name
from epa.models import kafka

from . import Handler


logger = epa.logging.get_logger(__name__)


class KafkaHandler(Handler):
    handler_id = "kafka"

    def __init__(self, *args, **kwargs):
        self._kafka = kafka.KafkaHandler(data_cls=None, **kwargs)
        self.result_proxy = None

    def read(self, size=1000, timeout=3.0):
        self.result_proxy = self._kafka.read()
        for ret in self.result_proxy.as_stream(size, timeout):
            yield from ret.as_list()

    def write(self, value):
        self._kafka.write(value)

    def close(self):
        if self.result_proxy:
            self.result_proxy.consumer.close()



class DataObjectKafkaHandler(Handler):
    handler_id = "kafka_dataobject"

    def __init__(self, model):
        self.data_class = get_class_with_name("epa.models", model)

    def read(self, size=1000, timeout=3.0):
        for ret in self.data_class.kafka.read().as_stream(size, timeout):
            yield from ret.as_list()

    def write(self, data):
        self.data_class.kafka.write(data)

