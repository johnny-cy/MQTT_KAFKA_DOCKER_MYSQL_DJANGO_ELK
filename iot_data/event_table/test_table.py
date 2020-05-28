#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import argparse
from datetime import datetime, timedelta
import random

import dateutil
import numpy as np
import pandas as pd

from epa.models import IoTRawData, IoTDevice, IoTEvent
from epa.area import all_areas

from epa.logging import get_logger

import requests
url = "https://iot.epa.gov.tw/iot/v1/device"
headers = {"CK": "PKWE7UWFZHXWEA2H2Z"}
res = requests.get(url=url,headers=headers)
targets = res.json()


STD_THRESHOLD = 2.7
logger = get_logger(__name__)
AREA = all_areas


def memory_usage_psutil():
    # return the memory usage in MB
    import os
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / float(2 ** 20)
    return mem


class DataHandler(object):
    def read(self):
        raise NotImplementedError

    def write(self, df):
        raise NotImplementedError


class BatchDataHandler(DataHandler):
    def __init__(self, start, end):
        self.data_class = IoTRawData
        self.start = start
        self.end = end
        self.batch_size = 100_000_000_000_000

    def read(self):
        yield from self.data_class.db.read(
            where=["time >= :start", "time <= :end"],
            sort=["time"],
            start=self.start,
            end=self.end,
        ).as_stream(batch_size=self.batch_size)

    def write(self, df):
        raise NotImplementedError("Don't call this method here.")


class StreamDataHandler(DataHandler):
    def __init__(self):
        self.data_class = IoTRawData

    def read(self):
        yield from self.data_class.kafka.read().as_stream()

    def write(self, df):
        raise NotImplementedError("Don't call this method here.")


class EventResultDataHandler(DataHandler):
    def __init__(self):
        self.data_class = IoTEvent

    def read(self):
        raise NotImplementedError("Don't call this method here.")

    def write(self, df):
        self.data_class.db.write(df)
        self.data_class.kafka.write(df)


class AreaEventDetector(object):
    def __init__(self, area, df_device):
        self.area = area
        self.df_device = df_device

        self._last_check_time = datetime(2000, 1, 1)
        self._random_check_interval()

    @property
    def name(self):
        return self.area.name

    def _rawdata_within_area(self, df):
        area = self.area
        df = df[
            (df["lon"] >= area.min_lon) &
            (df["lon"] <= area.max_lon) &
            (df["lat"] >= area.min_lat) &
            (df["lat"] <= area.max_lat)
        ]
        return df

    def _random_check_interval(self):
        self.check_interval = timedelta(seconds=random.randint(40, 90))

    def _exceed_check_interval(self, df):
        latest_data_time = df["time"].max()
        if latest_data_time - self._last_check_time >= self.check_interval:
            self._last_check_time = latest_data_time
            self._random_check_interval()
            return True
        else:
            return False

    def detect_events(self, df_rawdata):
        area = self.area
        df = self._rawdata_within_area(df_rawdata)
        if df.empty:
            return None
        if not self._exceed_check_interval(df):
            return None

        logger.debug(f"Area detect_events: {area.name}")

        df = df.drop_duplicates(["time", "device_id"])\
               .pivot(index="time", columns="device_id", values="pm2_5")\
               .resample("1T").first()\
               .interpolate(limit=30)
        df_interpolated_data = df.where(pd.notnull(df), None)

        # 1.
        s_mean = df.mean(axis=1)
        s_std = df.std(axis=1)
        df_std_err = df.copy()
        for col in df.columns:
            df_std_err[col] = (df[col] - s_mean) / s_std
        s_std_err = df_std_err.unstack().rename("STD err")

        # 2.
        df_rolling_mean = df.rolling('60T', min_periods=60).mean()
        df_rolling_std = df.rolling('60T', min_periods=60).std()

        s1 = df.unstack().rename("PM2.5")
        s2 = df_rolling_mean.unstack().rename("MEAN (60 min)")
        s3 = df_rolling_std.unstack().rename("STD (60 min)")

        df = pd.concat([s1, s2, s3, s_std_err], axis=1)
        df.index.names = ["Device Id", "Time"]
        # YK: s3 may be 0, divided by 0 issue
        df["STD err (60 min)"] = ((s1 - s2) / s3).replace(np.inf, 0)

        df = df[(df["STD err"] > STD_THRESHOLD) &
                (df["STD err (60 min)"] > STD_THRESHOLD) &
                (df["PM2.5"] > 45)]
        # DEBUGGGGGGGGing
        # df = df[df["PM2.5"] > 10]
        if df.empty:
            return None

        df = df.sort_index(level=1).reset_index()
        y = df["Time"].diff()

        cum_event = (y > timedelta(minutes=area.combine_minutes)).cumsum()

        df["Event Id"] = cum_event
        df["Event Count"] = y.groupby(cum_event).cumcount() + 1

        group = df.groupby("Event Id")
        df = pd.concat([
            group["Device Id"].unique(),
            group["Event Count"].max(),
            group["Time"].min(),
            group["Time"].max(),
            group["PM2.5"].max(),
        ], axis=1)
        df.columns = ["device_list", "event_count",
                      "start_time", "end_time", "max_value"]
        df["duration"] = (df["end_time"] - df["start_time"] +
                          timedelta(minutes=1)) / timedelta(minutes=1)
        df["area"] = area.name
        try:
            df["event_id"] = area.area_id + df["start_time"].dt.strftime("%Y%m%d%H%M%S")
        except AttributeError:
            pass

        def _device_info(row):
            if row.empty:
                return []
            device_list = row["device_list"]
            start, end = row["start_time"], row["end_time"]
            ret = []
            for x in device_list.tolist():
                try:
                    device = self.df_device.loc[x].to_dict()
                    device["pm2_5"] = df_interpolated_data.loc[start:end, x].tolist()
                    ret.append(device)
                except KeyError:    # x not in df_device.index
                    continue
            return ret
        df["device_list"] = df.apply(_device_info, axis=1)
        df["device_count"] = df["device_list"].apply(lambda x: len(x))
        df["min_lat"] = df["device_list"].apply(lambda l: min(x["lat"] for x in l))
        df["min_lon"] = df["device_list"].apply(lambda l: min(x["lon"] for x in l))
        df["max_lat"] = df["device_list"].apply(lambda l: max(x["lat"] for x in l))
        df["max_lon"] = df["device_list"].apply(lambda l: max(x["lon"] for x in l))
        first_device = df["device_list"].apply(
            lambda l: max((x for x in l),
                    key=lambda x: (x["pm2_5"][0] if x["pm2_5"] else -1) or -1
                )
            )[0]
        df["first_device"] = first_device["device_id"]
        df["first_value"] = first_device["pm2_5"][0]
        df["item"] = "pm2_5"
        df["score"] = df["duration"] * df["event_count"]
        df["level"] = df["score"].apply(
                lambda s: 3 if s >= 225 else
                          2 if s >= 100 else
                          1 if s >= 25 else
                          0
                )
        return df


class EventDetector(object):
    rawdata_time_buffer = timedelta(hours=4)
    event_time_buffer = timedelta(hours=2)

    def __init__(self):
        fields = ["device_id", "name", "lat", "lon"]
        df_device = IoTDevice.db.read(fields=fields)\
                                .as_df()\
                                .set_index("device_id", drop=False)
        self.areas = [AreaEventDetector(area, df_device) for area in AREA]

        self.df_rawdata = pd.DataFrame(columns=["time"])
        self.rawdata_time_buffer = EventDetector.rawdata_time_buffer
        self.event_time_buffer = EventDetector.event_time_buffer

    def run_detecting(self):
        self.input = StreamDataHandler()
        self.output = EventResultDataHandler()

        now = datetime.now()
        self._load_previous_data(now - timedelta(hours=4), now)

        self._run_detecting()

    def detect(self, start, end):
        start -= timedelta(hours=2) # data buffer
        end += timedelta(minutes=30) # data buffer
        self.input = BatchDataHandler(start, end)
        self.output = EventResultDataHandler()

        self.rawdata_time_buffer = timedelta(days=399_999)
        self.event_time_buffer = timedelta(days=399_999)

        logger.info(f"Start detecting event {start} to {end}...")
        self._run_detecting(start, end)
        logger.info("Finish.")

    def _run_detecting(self, 
            event_time_window_start=None,
            event_time_window_end=None):
        columns = ["time", "device_id", "name", "lat", "lon", "pm2_5"]

        rawdata_time_window = datetime(2000, 1, 1)
        event_time_window = event_time_window_start or datetime(2000, 1, 1)

        for data in self.input.read():
            df = data.as_df().copy(deep=True)
            li = list(df["device_id"])
            df.set_index("device_id", inplace=True)
            print("set_index..")
            for target in targets:
                if target["id"] in li:
                    df.loc[str(target["id"]), ["name","lat","lon"]] = target["name"], target["lat"], target["lon"]
            
            print("done targets...", end="")

            try:
                df.reset_index(inplace=True)
                df = df[columns]
                df.dropna(inplace=True)
            except KeyError:
                print("keyerror")
                continue
            if df.empty:
                print("df empty")
                continue

            # check the df maoli data
            # df[df[device_id=="9311298497"]]
            import pdb; pdb.set_trace()

            df["time"] = pd.to_datetime(df["time"])
            df["device_id"] = df["device_id"].astype(str)

            df = df[df["time"] > rawdata_time_window]

            self._merge_new_data(df)  
            
            for area in self.areas:
                df = area.detect_events(self.df_rawdata)
                
                if df is None or df.empty:
                    continue

                self._update_event_in_range(df, event_time_window,
                        event_time_window_end)

            self._keep_rawdata_after(rawdata_time_window)

            t = self.df_rawdata["time"].max().to_pydatetime()
            rawdata_time_window = t - self.rawdata_time_buffer
            event_time_window = t - self.event_time_buffer

    def _load_previous_data(self, start, end):
        reader = BatchDataHandler(start, end)
        dfs = []
        for data in reader.read():
            df = data.as_df()
            if not df.empty:
                dfs.append(df)
        if dfs:
            df = pd.concat(dfs)
            self.df_rawdata = df

    def _merge_new_data(self, df_new):
        self.df_rawdata = self.df_rawdata.append(df_new, sort=False)
        df = self.df_rawdata
        logger.debug(f"{df['time'].min()} -> {df['time'].max()} = "
                     f"{df['time'].max() - df['time'].min()}")
        logger.debug(f"memory usage: "
                     f"{df.memory_usage(deep=True).sum()/1048576:.2f} MB")

    def _keep_rawdata_after(self, time):
        df = self.df_rawdata
        df = df[df["time"] > time]
        self.df_rawdata = df

    def _update_event_in_range(self, df, start, end=None):
        df = df[df["end_time"] > start]
        if end:
            df = df[df["end_time"] < end]
        
        self.output.write(df)


first_run = True

def batch():
    global first_run
    now = datetime.now()

    if first_run:
        first_day = datetime(2018, 1, 1)
        first_run = False
    else:
        first_day = now - timedelta(days=30)

    span = timedelta(hours=4)
    
    t = datetime(now.year, now.month, now.day) - timedelta(days=13)
    t = t - span

    while t > first_day:
        t -= span
        start_time = t
        end_time = t + span
        logger.info(f"Batch event_table: {t}, {start_time}, {end_time}")

        EventDetector().detect(start_time, end_time)


def batch_loop():
    while True:
        batch()

        logger.info("Long sleep")
        time.sleep(6*60*60)


def main():
    parser = argparse.ArgumentParser(
        description="GuanYin PM2.5 peak detection",
    )
    parser.add_argument("-s", "--start",
                        help="start time: default: now - 3day")
    parser.add_argument("-e", "--end",
                        help="end time, default: now")
    parser.add_argument("-c", "--streaming", action='store_true',
                        help="streaming data")

    args = parser.parse_args()
    end = dateutil.parser.parse(args.end) if args.end else \
        datetime.now()
    start = dateutil.parser.parse(args.start) if args.start else \
        end - timedelta(days=3)

    event_detector = EventDetector()
    if args.streaming:
        event_detector.run_detecting()
    else:
        batch_loop()


if __name__ == "__main__":
    main()

