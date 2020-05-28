#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import time
import argparse
import datetime
import itertools
import math

import dateutil
import numpy as np
import pandas as pd
import geopy
import geopy.distance

import epa.logging
from epa.models import IoTRawData, IoTCircle

from epa.area import (Taichung,
    NewTaipei, Yilan, Taoyuan, Hsinchu, Miaoli, Yunlin, Chiayi,
    Tainan, Kaohsiung, Pingtung, Changhua, Keelung,
    )




url = "https://iot.epa.gov.tw/iot/v1/device"
headers = {"CK": "PKWE7UWFZHXWEA2H2Z"}
res = requests.get(url=url,headers=headers)
targets = res.json()


logger = epa.logging.get_logger(__name__)

CIRCLE_DISTANCE = 0.3


class NoMatchData(Exception):
    pass


class Point(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"({self.lat} {self.lon})"

    def __repr__(self):
        return self.__str__()


def circle_generator(area):
    point = Point(area.min_lat, area.min_lon)
    _, next_lat, _, next_lon = point_extend_distance(point, CIRCLE_DISTANCE)
    lat_diff = next_lat - area.min_lat
    lon_diff = next_lon - area.min_lon
    grid_lat_num = math.ceil((area.max_lat - area.min_lat) / lat_diff)
    grid_lon_num = math.ceil((area.max_lon - area.min_lon) / lon_diff)
    max_lat = area.min_lat + grid_lat_num * lat_diff
    max_lon = area.min_lon + grid_lon_num * lon_diff

    lat_edge = np.linspace(area.min_lat, max_lat, num=grid_lat_num)
    lon_edge = np.linspace(area.min_lon, max_lon, num=grid_lon_num)
    df = pd.DataFrame(list(itertools.product(lat_edge, lon_edge)),
                      columns=["lat", "lon"])
    df = df.reset_index().rename(columns={"index": "circle_idx"})
    return df


def point_extend_distance(point, distance):
    g = geopy.distance.geodesic(kilometers=distance)
    center = geopy.Point([point.lat, point.lon])
    min_lat = g.destination(center, 180).latitude
    max_lat = g.destination(center, 0).latitude
    min_lon = g.destination(center, 270).longitude
    max_lon = g.destination(center, 90).longitude
    return min_lat, max_lat, min_lon, max_lon


def point_in_mbr(df, min_lat, max_lat, min_lon, max_lon):
    """
    Return points which are located in Minimal Boundary Rectangle (MBR)
    """
    df = df[(df["lat"] >= min_lat) &
            (df["lat"] <= max_lat) &
            (df["lon"] >= min_lon) &
            (df["lon"] <= max_lon)
            ]
    return df


class CircleScorer(object):
    _data_object = IoTCircle

    def __init__(self, area_name, center_point, radius, time, circle_id):
        self.area_name = area_name
        self.time = time
        self.circle_id = circle_id

        self.center = center_point
        self.radius = radius

        self._min_lat, self._max_lat, self._min_lon, self._max_lon = \
            point_extend_distance(center_point, radius)

        self._dirty = False
        self._data_instance = None

    @property
    def score(self):
        if not self._data_instance:
            self.load()
        return self._data_instance.score

    @score.setter
    def score(self, new_score):
        if not self._data_instance:
            self.load()
        self._data_instance.score = new_score
        self._dirty = True

    def calculate_score(self, df, column="pm2_5", threshold=54):
        score = self._calculate_score(df, column, threshold)
        if score is not None:
            self.score = score

    def add_score(self, df, column="pm2_5", threshold=54):
        score = self._calculate_score(df, column, threshold)
        if score is not None and score > 0:
            self.score += score

    def _calculate_score(self, df, column="pm2_5", threshold=54):
        df = df[["time", "lat", "lon", column]]
        df = self._point_in_mbr(df)
        if df.empty:
            return None
        df = self._point_in_circle(df)
        if df.empty:
            return None
        score = (df[column] > threshold).sum()
        return score

    def save(self):
        if self._dirty and self._data_instance and self.score > 0:
            self._data_instance.save()
            self._dirty = False

    def load(self):
        self._data_instance = IoTCircle.load(where=[
            "time = :time",
            "area = :area",
            "circle_index = :circle_id"
        ], area=self.area_name, time=self.time, circle_id=self.circle_id)
        if self._data_instance is None:
            self._data_instance = IoTCircle(self.time,
                                            self.area_name,
                                            self.circle_id,
                                            0,
                                            self.center.lat,
                                            self.center.lon,
                                            self.radius)

    def _point_in_circle(self, df):
        """
        Return points which are located within circle radius
        """
        if df.empty:
            return df
        df = df[df.apply(self._is_point_in_range, axis=1)]
        return df

    def _is_point_in_range(self, row, distance=None):
        if distance is None:
            distance = self.radius
        x = (row["lat"], row["lon"])
        center = (self.center.lat, self.center.lon)
        return geopy.distance.geodesic(center, x).km < distance

    def _point_in_mbr(self, df):
        """
        Return points which are located in Minimal Boundary Rectangle (MBR)
        """
        if df.empty:
            return df
        df = df[(df["lat"] >= self._min_lat) &
                (df["lat"] <= self._max_lat) &
                (df["lon"] >= self._min_lon) &
                (df["lon"] <= self._max_lon)
                ]
        return df


class CircleController(object):
    def __init__(self, area, item="pm2_5"):
        self.df_circles = pd.DataFrame([],
                                       columns=["time", "circle_idx", "lat", "lon", "circle"])
        self.area = area
        self.item = item

        now = datetime.datetime.now()
        current_hour = datetime.datetime(
            now.year, now.month, now.day, now.hour)
        self._append_circle_with_time(current_hour)

    def load_circle(self, min_lat, max_lat, min_lon, max_lon, min_time, max_time):
        min_time = datetime.datetime(min_time.year, min_time.month,
                                     min_time.day, min_time.hour, 0, 0)
        max_time = datetime.datetime(max_time.year, max_time.month,
                                     max_time.day, max_time.hour, 0, 0)
        if min_time < self.df_circles["time"].min():
            t = self.df_circles["time"].min()
            delta = t - min_time
            for h in range(0, int(delta / datetime.timedelta(hours=1))):
                new_time = min_time + datetime.timedelta(hours=h)
                self._append_circle_with_time(new_time)
        if max_time > self.df_circles["time"].max():
            t = self.df_circles["time"].max()
            delta = max_time - t
            for h in range(1, int(delta / datetime.timedelta(hours=1)) + 1):
                new_time = t + datetime.timedelta(hours=h)
                self._append_circle_with_time(new_time)

        df = self.df_circles
        df = point_in_mbr(df, min_lat, max_lat, min_lon, max_lon)
        df = df[(df["time"] >= min_time) & (df["time"] <= max_time)]

        def _check_circle_object(row):
            if not row["circle"]:
                circle = CircleScorer(self.area.name,
                                      Point(row["lat"], row["lon"]),
                                      self.area.radius,
                                      row["time"],
                                      row["circle_idx"]
                                      )
                row["circle"] = circle
            return row
        df = df.apply(_check_circle_object, axis=1)
        return df

    def _append_circle_with_time(self, time):
        df = circle_generator(self.area)
        df["time"] = time
        df["circle"] = None
        self.df_circles = self.df_circles.append(df, sort=False)[["time", "circle_idx", "lat", "lon", "circle"]]

    def evaluate_stream(self, df_rawdata, threshold=54):
        try:
            df_circles, df_sub_data = self._evaluate(df_rawdata, threshold)
        except NoMatchData:
            return
        for circle in df_circles["circle"]:
            circle.add_score(df_sub_data, threshold=54)
            circle.add_score(df_sub_data, threshold=71)
            circle.save()

    def evaluate_batch(self, df_rawdata, threshold=54):
        try:
            df_circles, df_sub_data = self._evaluate(df_rawdata, threshold)
        except NoMatchData:
            print("df_circles, df_sub_data no match data..")
            return
        for circle in df_circles["circle"]:
            circle.calculate_score(df_sub_data, threshold=54)
            circle.add_score(df_sub_data, threshold=71)
            circle.save()

    def _evaluate(self, df_rawdata, threshold=54):
        df = df_rawdata
        li = list(df["device_id"])
        df.set_index("device_id", inplace=True)
        print("set_index..")
        #import pdb;pdb.set_trace()
        for target in targets:
            
            if target["id"] in li:
                #import pdb;pdb.set_trace()
                print(target["id"], end=",")
                df.loc[str(target["id"]), ["name","lat","lon"]] = target["name"], target["lat"], target["lon"]
               
        print("done targets...", end="")



        for col in ["time", "lat", "lon", self.item]:
            if col not in df.columns:
                raise NoMatchData

        df = point_in_mbr(df,
                          self.area.min_lat,
                          self.area.max_lat,
                          self.area.min_lon,
                          self.area.max_lon)
        
        if df.empty:
            raise NoMatchData

        df = df[df[self.item] >= threshold]
        if df.empty:
            raise NoMatchData

        df = df[["time", "lat", "lon", self.item]].dropna()
        if df.empty:
            raise NoMatchData

        min_lat = df["lat"].min()
        max_lat = df["lat"].max()
        min_lon = df["lon"].min()
        max_lon = df["lon"].max()
        min_time = df["time"].min()
        max_time = df["time"].max()
        
        df_sub_data = df

        point_1 = Point(min_lat, min_lon)
        point_2 = Point(max_lat, max_lon)
        radius = self.area.radius
        min_lat, _, min_lon, _ = point_extend_distance(point_1, radius)
        _, max_lat, _, max_lon = point_extend_distance(point_2, radius)

        df_circles = self.load_circle(min_lat, max_lat,
                                      min_lon, max_lon,
                                      min_time, max_time)
        print("return df_circles, df_sub_data")
        #import pdb; pdb.set_trace()
        # try df_circles see if there is ["circle"]
        return df_circles, df_sub_data


    def cleanup(self):
        _2_hours_ago = datetime.datetime.now() - datetime.timedelta(days=27) - datetime.timedelta(hours=2)
        df = self.df_circles
        df = df[df["time"] > _2_hours_ago]
        self.df_circles = df


def streaming(controllers):

    batch_size = 100_000
    timeout = 30
    for data in IoTRawData.kafka.read().as_stream(batch_size, timeout):
        df = data.as_df()

        if df.empty:
            continue

        df["time"] = pd.to_datetime(df["time"])
        now = datetime.datetime.now()
        oldest = now - datetime.timedelta(hours=4)
        df = df[(df["time"] > oldest) & (df["time"] < now)]
        if df.empty:
            continue

        for controller in controllers:
            controller.evaluate_stream(df)
            controller.cleanup()

first_run = True

def batch(controllers):
    global first_run
    now = datetime.datetime.now()

    if first_run:
        first_day = datetime.datetime(2018, 1, 1)
        first_run = False
    else:
        first_day = now - datetime.timedelta(days=50)
    t = datetime.datetime(now.year, now.month, now.day, 0, 0, 0) - \
        datetime.timedelta(days=27)

    while t > first_day:
        logger.info(f"historical batch: {t}")
        t -= datetime.timedelta(hours=1)
        start_time = t
        end_time = t + datetime.timedelta(hours=1)

        df = IoTRawData.db.read(
                where=[
                    "time >= :start_time",
                    "time < :end_time",
                ], 
                start_time=start_time,
                end_time=end_time,
            ).as_df()

        if df.empty:
            continue

        for controller in controllers:
            controller.evaluate_batch(df)
            controller.cleanup()


def batch_loop(controllers):
    while True:
        batch(controllers)

        logger.info("Long sleep")
        time.sleep(3*24*60*60)


def main():
    parser = argparse.ArgumentParser(
        description="Circle Hot Zone",
    )
    parser.add_argument("-s", "--start",
                        help="start time: default: now - 3day")
    parser.add_argument("-e", "--end",
                        help="end time, default: now")
    parser.add_argument("-c", "--streaming", action='store_true',
                        help="streaming data")

    args = parser.parse_args()
    end = dateutil.parser.parse(args.end) if args.end else \
        datetime.datetime.now()
    start = dateutil.parser.parse(args.start) if args.start else \
        end - datetime.timedelta(days=3)

    # TODO:
    # - [ ] datetime range mode
    # - [x] streaming mode

    controllers = [
        CircleController(area=Miaoli, item="pm2_5")
    ]

    if args.streaming:
        streaming(controllers)
    else:
        batch_loop(controllers)


if __name__ == "__main__":
    main()

