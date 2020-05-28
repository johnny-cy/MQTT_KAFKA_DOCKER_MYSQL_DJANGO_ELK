#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import epa.logging

from main import main_func
from coordinator import Coordinator


logger = epa.logging.get_logger("data_object")


class DataObject(Coordinator):
    pass


def main():
    main_func(DataObject,
              process_name="data_object",
              description="Move data object to Kafka queue"
              )


if __name__ == "__main__":
    main()


