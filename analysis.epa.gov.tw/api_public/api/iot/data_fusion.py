#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from dateutil import parser
from epa.models import LassRawData
from epa.models import TaichungPM25
import epa.logging


logger = epa.logging.get_logger(__name__)



def get(county=None, 
    start_time=None, 
    end_time=None,
    limit=10000,
        ):

    where_stmt = []
    param = {}

    end_time = parser.parse(end_time) if end_time \
        else datetime.datetime.now()
    start_time = parser.parse(start_time) if start_time \
        else end_time - datetime.timedelta(days=3)

    where_stmt.append("time >= :start_time")
    where_stmt.append("time <= :end_time")
    param["start_time"] = start_time
    param["end_time"] = end_time



    if county is not None:
        where_stmt.append("county = :county")
        param["county"] = county

    if limit > 10000:
        limit = 10000

    data = TaichungPM25.db.read(
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
