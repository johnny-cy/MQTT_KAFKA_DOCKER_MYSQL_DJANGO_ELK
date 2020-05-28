#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import epa.logging
from epa.models import IoTDevice


logger = epa.logging.get_logger(__name__)


def get(fields=[], device_ids=[], min_lat=None, max_lat=None, min_lon=None, max_lon=None):
    where_stmt = []
    param = {}

    if device_ids:
        where_stmt.append("device_id in :device_ids")
        param["device_ids"] = device_ids

    if min_lat is not None:
        where_stmt.append("lat >= :min_lat")
        param["min_lat"] = min_lat
    if max_lat is not None:
        where_stmt.append("lat <= :max_lat")
        param["max_lat"] = max_lat
    if min_lon is not None:
        where_stmt.append("lon >= :min_lon")
        param["min_lon"] = min_lon
    if max_lon is not None:
        where_stmt.append("lon <= :max_lon")
        param["max_lon"] = max_lon

    data = IoTDevice.db.read(
        fields=fields,
        where=where_stmt,
        **param,
    ).as_list()

    ret = {
        "count": len(data),
        "data": data,
        "errors": [],
    }
    return ret
