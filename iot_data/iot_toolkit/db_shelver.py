#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from main import main_func
from coordinator import Coordinator


class DBShelver(Coordinator):

    def reset(self):
        super().reset()

        self.postpone_write = self.config.postpone_write
        if self.postpone_write:
            self._queue = {}
            self._last_write = datetime.now()

    def pre_write(self, data):
        if not self.postpone_write:
            yield data
        else:
            yield from self.do_postpone_write(data)

    def do_postpone_write(self, data):
        key = tuple(data.keys())
        if key in self._queue:
            self._queue[key].append(data)
        else:
            self._queue[key] = [data]

        now = datetime.now()
        if now - self._last_write > timedelta(seconds=60):
            yield from self._queue.values()
            self._last_write = now
            self._queue = {}
        else:
            yield from []


def main():
    main_func(DBShelver,
              process_name="db_shelver",
              description="Shelve data from Kafka to DB",
              )


if __name__ == "__main__":
    main()

