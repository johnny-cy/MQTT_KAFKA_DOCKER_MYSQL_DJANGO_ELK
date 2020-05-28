#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from epa.utils import get_class_with_name, ClassNotFoundError


class Handler(object):
    handler_id = None

    def close(self):
        raise NotImplementedError

    def read(self):
        """
        Read one

        Parameters
        ----------
        None

        Returns
        -------
        generator with object
            JSON decoded object
        """
        raise NotImplementedError

    def write(self, value):
        """
        Write multi

        Parameters
        ----------
        value : object
            a JSON encodable object

        Returns
        -------
        None
        """
        raise NotImplementedError


def _get_py_module(dirname):
    for f in os.listdir(dirname):
        name, ext = os.path.splitext(f)
        if os.path.isfile(os.path.join(dirname, f)) and \
           ext == ".py" and \
           not name.startswith("__"):
            yield name


def get_handler_cls(handler_cls_name):
    for name in _get_py_module(os.path.dirname(__file__)):
        try:
            cls = get_class_with_name(f"handler.{name}", handler_cls_name)
            return cls
        except ClassNotFoundError:
            continue
    raise ClassNotFoundError
