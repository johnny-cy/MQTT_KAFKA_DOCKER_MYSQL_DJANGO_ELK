#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Every Coordinator have 1 input and 1 output

"""

import time
import threading
import queue
import os.path
from datetime import datetime

from epa.logging import get_logger

from configs import YamlConfig


metric_interval = 60
QUEUE_PUT_TIMEOUT = 120
QUEUE_GET_TIMEOUT = 60
logger = get_logger(__name__)


class Worker(threading.Thread):
    def __init__(self, handler, queue, pre_func, post_func, stop_event,
            *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = handler
        self.queue = queue
        self.pre_func = pre_func or nothing_func
        self.post_func = post_func or nothing_func
        self._stop_event = stop_event

        self.name = handler.name

        self._handled_count = 0
        self._droped_count = 0
        self._prev_reports = {
            "count": self._handled_count,
            "dropped": self._droped_count,
        }

    def start_metric_thread(self):
        name = type(self).__name__
        self.metric_thread = threading.Thread(target=self.metric_report,
                name=f"{self.name}.metric")
        self.metric_thread.start()

    def metric_report(self):
        while True:
            stopped = self._stop_event.wait(metric_interval)

            self._metric_report()

            if stopped:
                logger.warning("Stop metric_report().")
                break

    def _metric_report(self):
        curr_reports = {
            "count": self._handled_count,
            "dropped": self._droped_count,
        }
        reports = {
            "timestamp": datetime.now().isoformat(sep=" "),
            "handled": curr_reports["count"] - self._prev_reports["count"],
            "dropped": curr_reports["dropped"] - self._prev_reports["dropped"],
            "total_count": self._handled_count,
            "total_dropped": self._droped_count,
            "type": type(self).__name__,
            "name": self.name,
        }
        logger.metric(reports)

        self._prev_reports = curr_reports

    def update_count(self, x):
        if isinstance(x, list):
            self._handled_count += len(x)
        else:
            self._handled_count += 1

    def update_drop(self, x):
        if isinstance(x, list):
            self._droped_count += len(x)
        else:
            self._droped_count += 1

    def run(self):
        self.start_metric_thread()

        try:
            self.do_run()
        except Exception as e:
            logger.exception(e)
        finally:
            self._stop_event.set()

        logger.info(f"debug:print out the handler : \n{self.handler}")
        self.handler.close()


class Reader(Worker):

    def do_run(self):
        logger.info(f"Reader thread \"{self.name}\" starts running.")
        self.pre_func()
        for x in self.handler.read():
            for post_x in self.post_func(x): # generator
                if post_x:
                    try:
                        self.queue.put(post_x, timeout=QUEUE_PUT_TIMEOUT)
                        self.update_count(post_x)
                    except queue.Full:
                        logger.error(f"Queue is full, drop data.")
                        self.update_drop(post_x)

            if self._stop_event.is_set():
                logger.warning("Stop event is triggered")
                break
        logger.info(f"Reader thread \"{self.name}\" is over.")


class Writer(Worker):

    def do_run(self):
        logger.info(f"Writer thread \"{self.name}\" starts running.")
        while True:
            try:
                x = self.queue.get(timeout=QUEUE_GET_TIMEOUT)
                for pre_x in self.pre_func(x):
                    self.handler.write(pre_x)
                    post_x = self.post_func(pre_x)
                    self.update_count(post_x)
            except queue.Empty:
                logger.debug("Writer's queue is empty, go for next")

            if self._stop_event.is_set():
                logger.warning("Stop event triggered")
                break
        logger.info(f"Writer thread \"{self.name}\" is over.")


class Coordinator(threading.Thread):

    def __init__(self, config_file=None, queue_size=4096, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config_file = config_file
        self._queue_size = queue_size

    @property
    def stop_event(self):
        return self._stop_event

    def reset(self):
        cls_name = self.__class__.__name__
        self.config = YamlConfig(cls_name, self._config_file)

        if hasattr(self.config, "etl"):
            self.etl = self.config.etl

        self.queue = queue.Queue(self._queue_size)
        self._reader_thread = None
        self._writer_thread = None

        filename = os.path.split(self._config_file)[1]
        self.name = os.path.splitext(filename)[0]
        self._stop_event = threading.Event()
        self.terminated = False

    def run_reader_thread(self):
        handler = self.config.input
        t = Reader(handler, self.queue, self.pre_read, self.post_read,
                self._stop_event)
        logger.info(f"Reader thread \"{t.name}\" is created.")
        t.start()
        self._reader_thread = t

    def run_writer_thread(self):
        handler = self.config.output
        t = Writer(handler, self.queue, self.pre_write, self.post_write,
                self._stop_event)
        logger.info(f"Writer thread \"{t.name}\" is created.")
        t.start()
        self._writer_thread = t

    def run(self):
        self.run_forever()

    def run_forever(self):
        while True:
            self.reset()
            self._run()

            if self.terminated:
                break

            wait_seconds = 30
            logger.info(f"{self.name} ends. Try to respawn it after "
                        f"{wait_seconds} seconds")
            time.sleep(wait_seconds)

            if self.terminated:
                break

    def _run(self):
        logger.info(f"{type(self).__name__} {self.name} starts running.")
        self.run_writer_thread()
        self.run_reader_thread()

        self._stop_event.wait()

        self._reader_thread.join()
        self._writer_thread.join()

        logger.info("Coordinator's loop is over.")

    def pre_read(self):
        return

    def post_read(self, data):
        yield data

    def pre_write(self, data):
        yield data

    def post_write(self, data):
        return data

