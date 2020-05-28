#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from datetime import datetime, date, timedelta

import pandas as pd
from epa.utils import get_class_with_name
import epa.logging

from main import main_func
from coordinator import Coordinator


logger = epa.logging.get_logger("rawdata_updater")


class RawdataUpdater(Coordinator):
    url_template = ("https://iot.epa.gov.tw/iot/v1/device/{device_id}"
                    "/sensor/{sensor_id}/rawdata")
    earliest_day = date(2018, 1, 1)

    def reset(self):
        super().reset()

        self.project = self.config.project

        http_handler = self.config.input
        http_handler.url_delegate = self.url_delegator

        device_class = self.config.device_class
        data_class = self.config.data_class
        data_count_class = self.config.data_count_class
        self.device_class = get_class_with_name("epa.models", device_class)
        self.data_class = get_class_with_name("epa.models", data_class)
        self.data_count_class = get_class_with_name("epa.models", data_count_class)

        self.time_span_days = self.config.time_span_days
        if not isinstance(self.time_span_days, int):
            self.time_span_days = int(self.time_span_days)
            logger.warning(f"time_span_days isn't integer, use "
                           f"{self.time_span_days} instead.")

    def pre_read(self):
        http_handler = self.config.input
        http_handler.post_read_func = self.sleep_random_seconds

    def sleep_random_seconds(self, a=1, b=3):
        time.sleep(random.randint(a, b))

    def url_delegator(self):
        while True:
            yield from self._yield_url_headers_params()

            logger.info("Long sleep")
            self.sleep_random_seconds(12*60*60, 24*60*60)

    def _yield_url_headers_params(self):
        day = date.today()
        time_span = timedelta(days=self.time_span_days)
        while day > RawdataUpdater.earliest_day:
            day -= time_span
            start_time = datetime(day.year, day.month, day.day)
            end_time = start_time + time_span - timedelta(microseconds=1)

            yield from self._yield_by_ratio(start_time, end_time)

    def _yield_by_ratio(self, start_time, end_time, ratio=1.0):
        for device_id in self.project.devices:
            yield from self._filter_ratio(device_id,start_time,end_time, ratio)

    def _filter_ratio(self, device_id, start_time, end_time, ratio=1.0):
        s_count = self._get_data_count(device_id,
                start_time.date(), end_time.date())

        fields = list(s_count.index)
        s_db_count = self._calculate_data_in_db_count(device_id,
                fields, start_time, end_time)

        s_ratio = s_db_count.replace(0, 0.01) \
                            .divide(s_count, fill_value=0.1) \
                            .fillna(0)
        s_list = s_ratio[s_ratio < ratio].index.tolist()
        yield from self._yield(device_id, s_list, start_time, end_time)

    def _get_data_count(self, device_id, start_date, end_date):
        df = self.data_count_class.db.read(
                where=[
                    "date >= :start_date",
                    "date <= :end_date",
                    "device_id = :device_id"],
                start_date=start_date,
                end_date=end_date,
                device_id=device_id,
            ).as_df()
        drop_columns = ["date", "device_id", "_created_at", "_updated_at"]
        s_count = df.drop(drop_columns, axis=1).sum(min_count=1)
        return s_count

    def _calculate_data_in_db_count(self, device_id, fields,
            start_time, end_time):
        df = self.data_class.db.read(
                fields=fields,
                where=[
                    "time >= :start_time",
                    "time < :end_time",
                    "device_id = :device_id"
                    ],
                start_time=start_time,
                end_time=end_time,
                device_id=device_id,
            ).as_df()
        s_count = df.count()
        return s_count

    def _yield(self, device_id, sensors, start_time, end_time):
        device = self.device_class.load(where=[
            "device_id = :device_id"
            ], device_id=device_id)
        if not device:
            logger.warning(f"Device not found: {device_id}")
            yield from []
            return

        for sensor_id in sensors:
            if sensor_id not in device.sensors:
                logger.debug(f"{sensor_id} not in {device_id}, skip.")
                continue

            url = RawdataUpdater.url_template.format(device_id=device_id,
                                                     sensor_id=sensor_id)
            headers = {}
            params = {
                "start": f"{start_time:%Y-%m-%d %H:%M:%S.%f}",
                "end": f"{end_time:%Y-%m-%d %H:%M:%S.%f}",
            }
            yield url, headers, params
            logger.info(f"Yield: ({url}, {headers}, {params})")


def main():
    main_func(RawdataUpdater,
              process_name="rawdata_updater",
              description="Update rawdata from iot.epa.gov.tw",
              )


if __name__ == "__main__":
    main()
