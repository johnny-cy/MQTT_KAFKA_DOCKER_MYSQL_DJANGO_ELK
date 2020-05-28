#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" KafkaIOHandler

You can use local_settings.py to overwrite default kafka broker.

.. code-block:: python

   KAFKA_BROKER = "kafka:9092"

"""


import json
import collections.abc
from random import randint
import datetime

import pandas as pd
from confluent_kafka import Consumer, Producer
from confluent_kafka import KafkaException, KafkaError

from epa.logging import get_logger
from epa.models._data_io import DataIOHandler, DataResultProxy

try:
    from local_settings import KAFKA_BROKER
except (ModuleNotFoundError, ImportError):
    KAFKA_BROKER = "kafka:9092"


logger = get_logger(__name__)


def json_default(obj):
    """ json dumps default callback function
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat(sep=" ")
    elif isinstance(obj, datetime.date):
        return obj.isoformat()


def kafka_consumer_factory(config={}, topics=[]):
    """ The default Kafka consumer factory.

    This function will create a Consumer instance with properties ``config`` in
    which must contain `bootstrap.servers` and `group.id` at a minimum.

    Args
    ----
    config : dict, optional
        Configuration for Kafka consumer.
    topics : list(str), optional
        Topics to subscribe to. Regexp pattern subscriptions are supported.

    Returns
    -------
    confluent_kafka.Consumer
        Kafka consumer.
    """
    consumer = Consumer(config)
    consumer.subscribe(topics)
    logger.info(f"Create Kafka consumer for topics: {topics} "
                f"with config: {config}"
                )
    return consumer


class KafkaResultProxy(DataResultProxy):
    """ KafkaResultProxy

    Attributes
    ----------
    IGNORE_JSON_UNLOADABLE : bool, default ``True``
        If message value is not JSON loadable, skip it. Otherwise,
        json.decoder.JSONDecodeError will be raise.
    """

    IGNORE_JSON_UNLOADABLE = True

    def __init__(self, data_cls, consumer):
        """
        Args
        ----
        data_cls : DataObject
            Refer to DataObject.
        consumer : Kafka Consumer
            Kafka consumer.
        """
        self.data_cls = data_cls
        self.consumer = consumer

    def get_one(self, timeout=3.0):
        """ Get one result from kafka consumer.

        Args
        ----
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Returns
        -------
        dict or None
            Return ``dict`` object read from kafka topics.
            If timeout, ``None`` will be returned.
        """
        message = self.consumer.poll(timeout)
        ret = self._value_or_exception(message)
        return ret

    def get_object(self, timeout=3.0):
        """ Get one DataObject from kafka consumer.

        Args
        ----
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Returns
        -------
        DataObject or None
            Return ``DataObject`` read from kafka topics.
            If timeout, ``None`` will be returned.
        """
        one = self.get_one(timeout=timeout)
        return self.data_cls(**one) if one else None

    def as_list(self, limit=1000, timeout=3.0):
        """ Return a list of results which is key-value paired dict.

        Args
        ----
        limit : int, optional, default: 1000
            Limited batch size of returned list.
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Returns
        -------
        list
            List of results. Possibly less then 1000 results if timeout.
        """
        messages = self.consumer.consume(limit, timeout)
        ret = [self._value_or_exception(msg) for msg in messages]
        return ret

    def as_objects(self, limit=1000, timeout=3.0):
        """ Return a list of `DataObject` results.

        Args
        ----
        limit : int, optional, default: 1000
            Limited batch size of returned list.
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Returns
        -------
        list
            List of `DataObject` results. Possibly less then 1000 results if timeout.
        """
        result = self.as_list(limit=limit, timeout=timeout)
        return [self.data_cls(**x) for x in result]

    def as_df(self, limit=1000, timeout=3.0):
        """ Return a pandas DataFrame.

        Args
        ----
        limit : int, optional, default: 1000
            Limited batch size of returned list.
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame. Possibly less than 1000 results if timeout.
        """
        result = self.as_list(limit=limit, timeout=timeout)
        return pd.DataFrame(result)

    def as_stream(self, batch_size=1000, timeout=3.0):
        """ Yield streaming data results.

        Args
        ----
        limit : int, optional, default: 1000
            Limited batch size of returned list.
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Yields
        ------
        ``DataResultProxy``
        """
        while True:
            result = self.as_list(limit=batch_size, timeout=timeout)
            yield DataResultProxy(self.data_cls, result)

    def _value_or_exception(self, msg):
        if msg.error():
            error_code = msg.error().code()
            if error_code == KafkaError._TRANSPORT:
                logger.info("KafkaError._TRANSPORT, try again later.")
                return None
            elif error_code == KafkaError.GROUP_LOAD_IN_PROGRESS:
                logger.info("KafkaError.GROUP_LOAD_IN_PROGRESS, try again later.") 
                return None
            else:
                raise KafkaException(msg.error())

        try:
            return json.loads(msg.value())
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Can't decode json string: \"{msg.value()}\"")
            logger.exception(e)
            if not KafkaResultProxy.IGNORE_JSON_UNLOADABLE:
                raise


class KafkaHandler(DataIOHandler):
    """ KafkaHandler

    Everythin written to Kafka message queue is JSON string.

    Attributes
    ----------
    MAX_BUFFERING_MESSAGES : int
        Maximum buffer size for Kafka producer.
    default_config : dict
        Default Kafak config
    """

    MAX_BUFFERING_MESSAGES = 100_000
    default_config = {
        "bootstrap.servers": KAFKA_BROKER,
        "queue.buffering.max.ms": 1000,
        "queue.buffering.max.messages": MAX_BUFFERING_MESSAGES,
        "compression.codec": "lz4",
        "log.connection.close": False,
        "enable.partition.eof": False,
        "socket.keepalive.enable": True,
        "socket.timeout.ms": 300_000,
        "session.timeout.ms": 300_000,
        "fetch.wait.max.ms": 1000,
        'default.topic.config': {
            "compression.codec": "lz4",
            "compression.level": 12,
            "auto.offset.reset": "largest",
        }
    }

    def __init__(self, data_cls, topics, config={}):
        """
        Args
        ----
        data_cls : DataObject
            Refer to DataObject.
        topics : list(str)
            List of topics.
        config : dict, optional
            Extra configuration for Kafka producer/consumer.
        """
        self.data_cls = data_cls
        self.topics = topics

        default_config = KafkaHandler.default_config.copy()
        default_config.update(config)
        self._config = default_config

        self._consumer = None
        self._producer = None

    @property
    def producer(self):
        """ confluent_kafka.Producer : Kafka producer. """
        if self._producer is None:
            logger.debug(f"Create Kafka producer "
                         f"for topics: {self.topics} "
                         f"with config: {self._config}"
                         )
            self._producer = Producer(self._config)
        return self._producer

    def read(self, fields=[], where=[], sort=[], limit=None, offset=None,
            group_id=None, client_id=None, kafka_consumer_config={},
            consumer_factory=kafka_consumer_factory
            ):
        """ Read data from Kafka topics

        Args
        ----
        fields : list(str)
            This parameter has no effect in KafkaHandler
        where : list(str)
            This parameter has no effect in KafkaHandler
        sort : list(str)
            This parameter has no effect in KafkaHandler
        limit : int
            This parameter has no effect in KafkaHandler
        offset : int
            This parameter has no effect in KafkaHandler
        group_id : str, optional
            Kafka consumer group ID. If not set, a random string will be
            generated.
        client_id : str, optional
            Kafka consumer client ID. If not set, a random string will be
            generated.
        kafka_consumer_config : dict, optional
            Extra configuration for Kafka consumer. This value will be updated
            to KafkaHandler's config.
        consumer_factory : func, optional
            Factory function for generating consumer object. This function will
            take 2 options parameters, ``config`` and ``topics``.

        Returns
        -------
        KafkaResultProxy
        """
        if fields or where or sort or offset:
            logger.wraning(f"KafkaHandker doesn't support parameter: "
                           "fields, where, sort, limit, offset.")

        group_id = group_id or f"KafkaHandler.{randint(0, 9999999)}.group"
        client_id = client_id or f"KafkaHandler.{randint(0, 9999999)}.client"

        config = self._config.copy()
        config.update(kafka_consumer_config)
        config.update({
            "group.id": group_id, "client.id": client_id,
        })

        consumer = consumer_factory(config, self.topics)
        return KafkaResultProxy(self.data_cls, consumer)

    def write(self, data, wait=False):
        """ Write data to Kafka topics

        Args
        ----
        data : pd.DataFrame, list(object), anything json serialiable
            Data to be writen
        wait: bool, optional, default: False
            Wait for messages to be delivered.

        Returns
        -------
        None
        """
        if isinstance(data, pd.DataFrame):
            self._write_list(data.to_dict(orient="records"), wait)
        elif isinstance(data, (list, tuple)):
            self._write_list(data, wait)
        else:
            self._write_one(data, wait)

    def _write_list(self, values, wait=False):
        for value in values:
            self._write_one(value, wait)

    def _write_one(self, value, wait=False):
        json_str = json.dumps(value, default=json_default)
        for topic in self.topics:
            self.producer.produce(topic, json_str)

        if wait or(len(self.producer) / self.MAX_BUFFERING_MESSAGES) > 0.8:
            self.flush_producer(10.0)

    def flush_producer(self, timeout=3.0):
        """ Wait for all messages in the Producer queue to be delivered.

        Args
        ----
        timeout : float, optional, default: 3.0
            Maximum timeout to wait for message.

        Returns
        -------
        None
        """
        self.producer.flush(timeout)

