#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

from epa.models._data_object import DataObject
from epa.models.sqlalchemy import sensor_fusion




@dataclass
class TaichungPM25(DataObject):
    time: datetime = None
    county: str = None
    section_index: int = None
    pm25: float = None
    min_lon: float = None
    max_lon: float = None
    min_lat: float = None
    max_lat: float = None

    _sqlalchemy_cls = sensor_fusion.TaichungPM25
    _kafka_topic = "data_object.sensor_fusion.TaichungPM25"
