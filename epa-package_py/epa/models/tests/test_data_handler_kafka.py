#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock
import logging

import pandas as pd

from epa.models.iot import IoTDevice
from epa.models.kafka import KafkaHandler


class TestIoTDevice_Kafka(unittest.TestCase):

    def setUp(self):
        logging.disable(logging.DEBUG)
        IoTDevice.kafka = KafkaHandler(
            data_cls=Mock(),
            topics=[f"unittest.iot_device"],
            config={
                "queue.buffering.max.ms": 1,
                'default.topic.config': {
                    "offset.store.sync.interval.ms": 0,
                }
            },
        )
        self.data = [
            {"device_id": "1", "name": "name01", "desc": "desc01"},
            {"device_id": "2", "name": "name02", "desc": "desc02"},
            {"device_id": "3", "name": "name03", "desc": "desc03"},
            {"device_id": "4", "name": "name101", "desc": "desc04"},
            {"device_id": "5", "name": "name101", "desc": "desc05"},
        ]

        self.result_proxy = IoTDevice.kafka.read()
        self.result_proxy.as_list(timeout=0.2)

    def test_kafka_write(self):
        IoTDevice.kafka.write(self.data, wait=True)
        ret = self.result_proxy.as_list(timeout=0.2)
        self.assertEqual(len(ret), 5)

    def test_kafka_read(self):
        IoTDevice.kafka.write(self.data, wait=True)
        ret = self.result_proxy.as_list(timeout=0.2)
        self.assertEqual(ret, self.data)

    def test_kafka_read_as_df(self):
        IoTDevice.kafka.write(self.data, wait=True)
        df = self.result_proxy.as_df(timeout=0.2)
        self.assertTrue(df.equals(pd.DataFrame(self.data)))

    def test_kafka_read_as_stream(self):
        IoTDevice.kafka.write(self.data, wait=True)

        stream = self.result_proxy.as_stream(batch_size=10, timeout=0.2)
        for ret in stream:
            result = ret.as_list()
            # One batch
            self.assertEqual(result, self.data)
            break

    def test_kafka_read_as_stream_batch(self):
        IoTDevice.kafka.write(self.data, wait=True)

        stream = self.result_proxy.as_stream(batch_size=2, timeout=0.2)
        final_result = []
        count = 0
        for ret in stream:
            result = ret.as_list()
            if len(result) == 0:
                break
            final_result.extend(result)
            count += 1
        self.assertEqual(final_result, self.data)
        self.assertEqual(count, 3)


if __name__ == '__main__':
    unittest.main()
