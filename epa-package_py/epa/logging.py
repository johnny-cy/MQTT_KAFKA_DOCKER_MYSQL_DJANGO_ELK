#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging


METRIC = 19


class CameoLogger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

    def metric(self, value):
        """ Log 'value' with severity 'METRIC'.

        Args
        ----
        value : dict
            key-value paried dict to logged as metric.
        """
        if self.isEnabledFor(METRIC):
            self.log(METRIC, value)


logging.addLevelName(METRIC, "METRIC")
logging.setLoggerClass(CameoLogger)


def get_logger(name, level=logging.INFO):
    if os.environ.get("DEBUG"):
        level = logging.DEBUG

    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    f = "%(asctime)s %(name)s:%(lineno)d %(threadName)s %(levelname)s\t] %(message)s"
    handler.setFormatter(logging.Formatter(f))

    logger.addHandler(handler)
    return logger
