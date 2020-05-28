#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import epa.logging

from main import main_func
from coordinator import Coordinator
from etl_functions import ETLMixin


logger = epa.logging.get_logger("es_shelver")


class ESShelver(Coordinator, ETLMixin):

    def reset(self):
        super().reset()

        self.postpone_write = self.config.postpone_write
        self.postpone_gather_keys = self.config.postpone_gather_keys
        if self.postpone_write:
            self._queue = {}
            self._last_write = datetime.now()

    def post_read(self, data):
        yield from self.etl_value(data)

    def pre_write(self, data):
        if not self.postpone_write:
            yield data
        else:
            yield from self.do_postpone_write(data)

    def do_postpone_write(self, data):
        key = tuple(data[k] for k in self.postpone_gather_keys)
        if key in self._queue:
            self._queue[key].update(data)
        else:
            self._queue[key] = data

        now = datetime.now()
        if now - self._last_write > timedelta(seconds=60):
            yield list(self._queue.values())
            self._last_write = now
            self._queue = {}
        else:
            yield from []


def main():
    main_func(ESShelver,
              process_name="es_shelver",
              description="Shelve data from Kafka to Elasticsearch",
              )


if __name__ == "__main__":
    main()


