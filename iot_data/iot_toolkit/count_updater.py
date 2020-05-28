#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from datetime import date, timedelta

import epa.logging

from main import main_func
from coordinator import Coordinator


logger = epa.logging.get_logger("count_updater")


class CountUpdater(Coordinator):
    url_template = ("https://iot.epa.gov.tw/iot/v1/count/"
                    "project/{project_id}/sensor/{sensor_id}")
    earliest_day = date(2018, 1, 1)

    def reset(self):
        super().reset()

        http_handler = self.config.input
        http_handler.url_delegate = self.url_delegator

        self.data_class = self.config.output.data_class
        self.sensors = self.config.project.sensors

    def pre_read(self):
        http_handler = self.config.input
        http_handler.post_read_func = self.sleep_random_seconds

    def post_read(self, data):
        date = data["startTime"]
        sensor_id = data["sensorName"]
        for device_id, count in data["deviceCountMap"].items():
            yield {
                "date": date,
                "device_id": device_id,
                sensor_id: count,
            }

    def sleep_random_seconds(self, a=10, b=100):
        time.sleep(random.randint(a, b))

    def url_delegator(self):
        while True:
            yield from self._yield_url_headers_params()

            logger.info("Long sleep")
            self.sleep_random_seconds(12*60*60, 24*60*60)

    def _yield_url_headers_params(self):
        day = date.today()
        while day > CountUpdater.earliest_day:
            day -= timedelta(days=1)

            df = self.data_class.db.read(where=[
                "date = :day",
            ], day=day).as_df()

            if df.empty:
                yield from self._yield(day, self._get_df_sensors(df))
                continue

            unknown_sensors = self._null_count(df)
            if unknown_sensors:
                yield from self._yield(day, unknown_sensors)
                continue

            old_update = self._last_update(df)
            if old_update:
                yield from self._yield(day, old_update)
                continue

    def _get_df_sensors(self, df):
        drop_columns = ["date", "device_id", "_created_at", "_updated_at"]
        return df.drop(drop_columns, axis=1).columns.tolist()

    def _yield(self, day, sensors):
        project_id = self.config.project.code
        for sensor_id in sensors:
            url = CountUpdater.url_template.format(project_id=project_id,
                                                   sensor_id=sensor_id)
            headers = {}
            params = {
                "start": f"{day:%Y-%m-%d} 00:00:00",
                "end": f"{day:%Y-%m-%d} 23:59:59",
            }
            yield url, headers, params
            logger.info(f"Yield: ({url}, {headers}, {params})")

    def _null_count(self, df):
        drop_columns = ["date", "device_id", "_created_at", "_updated_at"]
        df = df.drop(drop_columns, axis=1)
        s = df.isnull().any()
        return s[s].index.tolist()

    def _last_update(self, df):
        today = date.today()
        create_time = df["_created_at"].min().to_pydatetime().date()
        last_update = df["_updated_at"].min().to_pydatetime().date()
        if today - create_time < timedelta(days=45) and \
           today - last_update > timedelta(days=7):
            return self._get_df_sensors(df)
        else:
            return []


def main():
    main_func(CountUpdater,
              process_name="count_updater",
              description="Update count of device sensor from iot.epa.gov.tw",
              )


if __name__ == "__main__":
    main()
