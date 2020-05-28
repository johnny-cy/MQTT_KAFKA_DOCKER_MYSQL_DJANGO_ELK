#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from epa.utils import get_class_with_name
from epa.logging import get_logger

from . import Handler


logger = get_logger(__name__)


class SqlAlchemyHandler(Handler):
    def __init__(self, model):
        self.data_class = get_class_with_name("epa.models", model)

    def write(self, value):
        try:
            self.data_class.db.write(value)
        except Exception as e:
            raise

    def close(self):
        pass

