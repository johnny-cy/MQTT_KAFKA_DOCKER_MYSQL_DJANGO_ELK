#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import epa.logging

from main import main_func
from coordinator import Coordinator
from etl_functions import ETLMixin


logger = epa.logging.get_logger("rest_etl")


class RESTETLer(Coordinator, ETLMixin):

    def post_read(self, data):
        yield from self.etl_value(data)


def main():
    main_func(RESTETLer,
              process_name="rest_etl",
              description="REST ETL"
              )


if __name__ == "__main__":
    main()


