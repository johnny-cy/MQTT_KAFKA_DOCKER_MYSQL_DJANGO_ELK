#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from dateutil import parser
from epa.models import IoTEvent
import epa.logging


logger = epa.logging.get_logger(__name__)


def get(area=None, start_time=None, end_time=None,
        min_lat=None, min_lon=None, max_lat=None, max_lon=None,
        limit=10000,
        ):

    where_stmt = []
    param = {}
    if area is not None:
        where_stmt.append("area = :area")
        param["area"] = area
    end_time = parser.parse(end_time) if end_time \
        else datetime.datetime.now()
    start_time = parser.parse(start_time) if start_time \
        else end_time - datetime.timedelta(days=3)
    where_stmt.append("start_time >= :start_time")
    where_stmt.append("end_time <= :end_time")
    param["start_time"] = start_time
    param["end_time"] = end_time

    if min_lat is not None:
        where_stmt.append("max_lat >= :min_lat")
        param["min_lat"] = min_lat
    if min_lon is not None:
        where_stmt.append("max_lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lat is not None:
        where_stmt.append("min_lat <= :max_lat")
        param["max_lat"] = max_lat
    if max_lon is not None:
        where_stmt.append("min_lon <= :max_lon")
        param["max_lon"] = max_lon

    if limit > 10000:
        limit = 10000

    fields = ["uid", "event_id", "area", "start_time", "end_time", "duration",
              "event_count", "max_value", "device_count", "device_list",
              "first_device", "first_value", "item", "score", "level",
              ]
    data = IoTEvent.db.read(
        fields=fields,
        where=where_stmt,
        limit=limit,
        **param,
    ).as_list()

    k1 = "device_id"
    k2 = "name"
    for e in data:
        d_list = e["device_list"]
        e["device_list"] = [{k1: d[k1], k2: d[k2]} for d in e["device_list"] ]

    ret = {
        "count": len(data),
        "data": data,
        "errors": [],
    }
    return ret


def get_earliest(area=None,
        min_lat=None, min_lon=None, max_lat=None, max_lon=None,
        ):
    where_stmt = []
    param = {}

    if area:
        where_stmt.append("area = :area")
        param["area"] = area

    if min_lat is not None:
        where_stmt.append("max_lat >= :min_lat")
        param["min_lat"] = min_lat
    if min_lon is not None:
        where_stmt.append("max_lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lat is not None:
        where_stmt.append("min_lat <= :max_lat")
        param["max_lat"] = max_lat
    if max_lon is not None:
        where_stmt.append("min_lon <= :max_lon")
        param["max_lon"] = max_lon

    fields = ["uid", "event_id", "area", "start_time", "end_time", "duration",
              "event_count", "max_value", "device_count", "device_list",
              "first_device", "first_value", "item", "score", "level",
              ]
    data = IoTEvent.db.read(
        fields=fields,
        where=where_stmt,
        sort=["start_time"],
        limit=1,
        **param,
    ).get_one()

    k1 = "device_id"
    k2 = "name"
    data["device_list"] = [{k1: d[k1], k2: d[k2]} for d in data["device_list"] ]

    ret = {
        "count": 1 if data else 0,
        "data": data if data else {},
        "errors": [],
    }
    return ret


def get_event_counts(area=None, start_time=None, end_time=None,
        min_level=None, max_level=None,
        min_lat=None, min_lon=None, max_lat=None, max_lon=None,
        ):
    where_stmt = []
    param = {}

    if area:
        where_stmt.append("area = :area")
        param["area"] = area

    end_time = parser.parse(end_time) if end_time \
        else datetime.datetime.now()
    start_time = parser.parse(start_time) if start_time \
        else end_time - datetime.timedelta(days=3)
    where_stmt.append("start_time >= :start_time")
    where_stmt.append("end_time <= :end_time")
    param["start_time"] = start_time
    param["end_time"] = end_time

    if min_level is not None:
        where_stmt.append("level >= :min_level")
        param["min_level"] = min_level
    if max_level is not None:
        where_stmt.append("level <= :max_level")
        param["max_level"] = max_level

    if min_lat is not None:
        where_stmt.append("max_lat >= :min_lat")
        param["min_lat"] = min_lat
    if min_lon is not None:
        where_stmt.append("max_lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lat is not None:
        where_stmt.append("min_lat <= :max_lat")
        param["max_lat"] = max_lat
    if max_lon is not None:
        where_stmt.append("min_lon <= :max_lon")
        param["max_lon"] = max_lon

    fields = ["area", "event_id"]
    df = IoTEvent.db.read(
        fields=fields,
        where=where_stmt,
        **param,
    ).as_df()

    df = df.groupby("area").count() \
           .rename(columns={"event_id": "counts"}) \
           .reset_index()

    ret = {
        "count": len(df),
        "data": df.to_dict(orient="records"),
        "errors": [],
    }
    return ret




