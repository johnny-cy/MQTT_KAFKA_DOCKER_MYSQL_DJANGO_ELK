#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import datetime
import time
import zlib
import struct

import dateutil.parser
from flask import stream_with_context
from flask import Response
from connexion import NoContent
import pandas as pd

import epa.logging
from epa.models import IoTRawData


logger = epa.logging.get_logger(__name__)


def _get_interpolated_df(start, end, fields, resample="1min",
                         min_lat=None, max_lat=None, min_lon=None, max_lon=None):
    where_stmt = [
        "time >= :start",
        "time < :end",
    ]
    param = {"start": start, "end": end}
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

    df = IoTRawData.db.read(fields=fields,
                            where=where_stmt,
                            **param,
                            ).as_df()

    if df.empty:
        return df

    df = df.set_index("time")\
           .groupby("device_id")\
           .resample(resample)\
           .first()\
           .drop("device_id", axis=1)\
           .interpolate(limit=10)
    df = df.where(pd.notnull(df), None)
    return df.reset_index()[fields]


def generate_gzip(start, end, fields, **param):
    # Yield a gzip file header first.
    yield (
        b'\037\213\010\000' +  # Gzip file, deflate, no filename
        struct.pack('<L', int(time.time())) +  # compression start time
        b'\002\377'  # maximum compression, no OS specified
    )

    # bookkeeping: the compression state, running CRC and total length
    compressor = zlib.compressobj(
        9, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0)
    crc = zlib.crc32(b"")
    length = 0

    s = start
    time_span = datetime.timedelta(hours=6)
    while s < end:
        e = s + time_span
        if e > end:
            e = end
        df = _get_interpolated_df(s, e, fields, **param)
        s = e
        if df.empty:
            continue

        si = io.StringIO()
        if length == 0:
            df.to_csv(si, index=False, header=True)
        else:
            df.to_csv(si, index=False, header=False)

        data = si.getvalue().encode()
        chunk = compressor.compress(data)
        if chunk:
            yield chunk
        crc = zlib.crc32(data, crc) & 0xffffffff
        length += len(data)

    # Finishing off, send remainder of the compressed data, and CRC and length
    yield compressor.flush()
    yield struct.pack("<2L", crc, length & 0xffffffff)


def get(fields=[], start_time=None, end_time=None,
        min_lat=None, max_lat=None, min_lon=None, max_lon=None,
        resample="1min", return_format="json"):
    now = datetime.datetime.now()
    _3_hours_ago = now - datetime.timedelta(hours=3)
    end_time = dateutil.parser.parse(end_time) if end_time else now
    start_time = dateutil.parser.parse(
        start_time) if start_time else _3_hours_ago

    # default columns
    fields = ["time", "device_id", "name", "lat", "lon"] + fields
    param = {"min_lat": min_lat, "max_lat": max_lat,
             "min_lon": min_lon, "max_lon": max_lon, }

    if return_format == "csv":
        response = Response(
            stream_with_context(generate_gzip(
                start_time, end_time, fields, resample, **param)),
            mimetype="application/gzip"
        )
        response.headers["Content-Disposition"] = "attachment; filename=export.csv.gz"
        return response
    elif return_format == "json":
        df = _get_interpolated_df(
            start_time, end_time, fields, resample, **param)
        ret = {
            "count": len(df),
            "data": df.to_dict(orient="records"),
            "errors": [],
        }
        return ret
    return NoContent, 404
