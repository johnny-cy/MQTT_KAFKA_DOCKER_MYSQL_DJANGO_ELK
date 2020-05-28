#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import importlib
from inspect import isclass
from functools import wraps

from epa import logging


logger = logging.get_logger(__name__)


class ClassNotFoundError(Exception):
    """Class not found in module"""

    def __init__(self, module_name, class_name):
        self.module_name = module_name
        self.class_name = class_name


def get_class_with_name(module_name, class_name):
    module = importlib.import_module(module_name)
    attrs = [a for a in dir(module) if not a.startswith("__")]
    for attr in attrs:
        x = getattr(module, attr)
        if isclass(x) and x.__name__ == class_name:
            return x
    raise ClassNotFoundError(module_name, class_name)


def timer(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        logger.info(f"Timer: {te-ts:2.4f} sec"
                    f" {{ {f.__name__} args: [{args}, {kw}] }}")
        return result
    return wrap
