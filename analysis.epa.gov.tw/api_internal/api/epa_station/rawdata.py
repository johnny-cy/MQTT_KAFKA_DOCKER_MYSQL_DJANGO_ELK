#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

import dateutil.parser
import epa.logging
from epa.models import EpaStationRawData


logger = epa.logging.get_logger(__name__)


def get(fields=[], start_time=None, end_time=None,
        min_lat=None, max_lat=None, min_lon=None, max_lon=None):
    now = datetime.datetime.now()
    _3_days_ago = now - datetime.timedelta(hours=3)
    end_time = dateutil.parser.parse(end_time) if end_time else now
    start_time = dateutil.parser.parse(
        start_time) if start_time else _3_days_ago

    # default columns
    fields = ["time", "device_id", "name", "lat", "lon"] + fields
    param = {"min_lat": min_lat, "max_lat": max_lat,
             "min_lon": min_lon, "max_lon": max_lon, }

    where_stmt = [
        "time >= :start_time",
        "time < :end_time",
    ]
    param = {"start_time": start_time, "end_time": end_time}

    if min_lat:
        where_stmt.append("lat >= :min_lat")
        param["min_lat"] = min_lat
    if max_lat:
        where_stmt.append("lat <= :max_lat")
        param["max_lat"] = max_lat
    if min_lon:
        where_stmt.append("lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lon:
        where_stmt.append("lon <= :max_lon")
        param["max_lon"] = max_lon

    data = EpaStationRawData.db.read(fields=fields,
                                     where=where_stmt,
                                     **param,
                                     ).as_list()

    ret = {
        "count": len(data),
        "data": data,
        "errors": [],
    }
    return ret
