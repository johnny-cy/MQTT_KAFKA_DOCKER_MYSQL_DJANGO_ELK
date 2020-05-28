#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from dateutil import parser
from epa.models import EpaStationTextarAbnormal
import epa.logging


logger = epa.logging.get_logger(__name__)


def get(stations=[], start_time=None, end_time=None, level=["M", "H"], limit=10000):

    where_stmt = []
    param = {}

    if stations:
        where_stmt.append("station IN :stations")
        param["stations"] = stations

    end_time = parser.parse(end_time) if end_time \
        else datetime.datetime.now()
    start_time = parser.parse(start_time) if start_time \
        else end_time - datetime.timedelta(days=1)
    where_stmt.append("time >= :start_time")
    where_stmt.append("time <= :end_time")
    param["start_time"] = start_time
    param["end_time"] = end_time

    where_stmt.append("level IN :level")
    param["level"] = level

    if limit > 10000:
        limit = 10000

    fields = ["time", "station", "level"]
    data = EpaStationTextarAbnormal.db.read(
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
