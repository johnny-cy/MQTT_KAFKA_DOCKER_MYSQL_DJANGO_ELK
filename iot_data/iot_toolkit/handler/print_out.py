#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import Handler


class PrintHandler(Handler):
    def write(self, value):
        print(value)

