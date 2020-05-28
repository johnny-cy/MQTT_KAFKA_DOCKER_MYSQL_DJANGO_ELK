#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List

from epa.models._data_object import DataObject
from epa.models.sqlalchemy import lass


@dataclass
class LassDevice(DataObject):
    device_id: str
    name: str = None
    desc: str = None
    type: str = None
    lat: float = None
    lon: float = None
    alt: float = None
    reference: bool = None
    display: bool = None
    device_type: str = None
    owner_id: str = None
    mobile: bool = None
    outdoor: bool = None
    manufacturer_id: str = None
    sensors: List[str] = None

    _sqlalchemy_cls = lass.LassDevice
    _kafka_topic = "data_object.lass_device"


@dataclass
class LassRawData(DataObject):
    time: datetime
    device_id: str
    name: str = None
    lat: float = None
    lon: float = None

    humidity: float = None
    pm2_5: float = None
    pm10: float = None
    temperature: float = None

    _sqlalchemy_cls = lass.LassRawData
    _kafka_topic = "data_object.lass_rawdata"


@dataclass
class LassRawDataCount(DataObject):
    date: date
    device_id: str

    humidity: int = None
    pm2_5: int = None
    pm10: int = None
    temperature: int = None

    _sqlalchemy_cls = lass.LassRawDataCount
    _kafka_topic = "data_object.lass_rawdata.count"

