#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import datetime

from dateutil import parser
import geopy.distance
from epa.models import IoTCircle
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
    where_stmt.append("time >= :start_time")
    where_stmt.append("time <= :end_time")
    param["start_time"] = start_time
    param["end_time"] = end_time

    if min_lat is not None:
        where_stmt.append("lat >= :min_lat")
        param["min_lat"] = min_lat
    if min_lon is not None:
        where_stmt.append("lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lat is not None:
        where_stmt.append("lat <= :max_lat")
        param["max_lat"] = max_lat
    if max_lon is not None:
        where_stmt.append("lon <= :max_lon")
        param["max_lon"] = max_lon

    if limit > 10000:
        limit = 10000

    fields = ["time", "area", "circle_index", "score", "lat", "lon", "radius"]
    data = IoTCircle.db.read(
        fields=fields,
        where=where_stmt,
        limit=limit,
        **param,
    ).as_list()

    ret = {
        "count": len(data),
        "data": data,
        "errors": [],
    }
    return ret


def avg(area=None, start_time=None, end_time=None,
        min_lat=None, min_lon=None, max_lat=None, max_lon=None,
        score_threshold=None, limit=10000,
        ):

    errors = []
    where_stmt = []
    param = {}
    limit = int(limit)

    if area is not None:
        where_stmt.append("area = :area")
        param["area"] = area

    end_time = parser.parse(end_time) if end_time \
        else datetime.datetime.now()
    start_time = parser.parse(start_time) if start_time \
        else end_time - datetime.timedelta(days=3)
    where_stmt.append("time >= :start_time")
    where_stmt.append("time <= :end_time")
    param["start_time"] = start_time
    param["end_time"] = end_time

    if min_lat is not None:
        where_stmt.append("lat >= :min_lat")
        param["min_lat"] = min_lat
    if min_lon is not None:
        where_stmt.append("lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lat is not None:
        where_stmt.append("lat <= :max_lat")
        param["max_lat"] = max_lat
    if max_lon is not None:
        where_stmt.append("lon <= :max_lon")
        param["max_lon"] = max_lon

    if limit > 10000:
        limit = 10000

    if score_threshold is None:
        point1 = (min_lat, min_lon)
        point2 = (max_lat, max_lon)
        distance = geopy.distance.distance(point1, point2).km
        score_threshold = 40 if distance > 50 else \
                          20 if distance > 20 else \
                          0
    where_stmt.append("score >= :score_threshold")
    param["score_threshold"] = score_threshold

    hard_limit = 100_000
    total_hours = math.ceil((end_time - start_time).total_seconds() / 3600)
    fields = ["time", "area", "circle_index", "score", "lat", "lon", "radius"]

    df = IoTCircle.db.read(
        fields=fields,
        where=where_stmt,
        limit=hard_limit, # hard limit to 100k, only constraints 10k in return
        **param,
    ).as_df()

    if len(df) >= hard_limit:
        errors += ["Query too much data, only part of them are taken. "
                   "The result may be inaccurate."]

    if df.empty:
        errors += ["No data found."]
        return {"count": 0,
                "start_time": start_time,
                "end_time": end_time,
                "total_hours": total_hours,
                "data": [],
                "errors": errors}

    df2 = df[["time", "area", "circle_index", "score"]] \
            .set_index("time") \
            .groupby(["area", "circle_index"]) \
            .sum()
    df2 /= total_hours
    df2.columns = [f"score avg"]

    df3 = df[["area", "circle_index", "lat", "lon", "radius"]] \
            .drop_duplicates() \
            .set_index(["area", "circle_index"])
    df4 = df2.merge(df3, how="left", left_index=True, right_index=True) \
             .reset_index()

    if len(df4) >= limit:
        df4 = df4.iloc[:limit]
        errors += [f"Result exceeds {limit}."]

    ret = {
        "count": len(df4),
        "start_time": start_time,
        "end_time": end_time,
        "total_hours": total_hours,
        "data": df4.to_dict(orient="records"),
        "errors": errors,
    }
    return ret
