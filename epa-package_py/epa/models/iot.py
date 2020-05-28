#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Any

from epa.models._data_object import DataObject
from epa.models.sqlalchemy import iot


@dataclass
class IoTDevice(DataObject):
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
    mac_id: str = None
    devstat: str = None
    sb_id: str = None
    mb_id: str = None
    errorcode: str = None
    area: str = None
    areatype: str = None
    # YK: object has no attribute 'sensors' in __init__(), work-around
    # sensors: list = field(default_factory=list)
    sensors: List[str] = None

    _sqlalchemy_cls = iot.IoTDevice
    _kafka_topic = "data_object.iot_device"


@dataclass
class IoTRawData(DataObject):
    time: datetime
    device_id: str
    name: str = None
    lat: float = None
    lon: float = None

    ampere: float = None
    co: float = None
    devstat: float = None
    humidity: float = None
    humidity_main: float = None
    no2: float = None
    noise: float = None
    o3: float = None
    pm1: float = None
    pm2_5: float = None
    pm10: float = None
    temperature: float = None
    temperature_main: float = None
    voc: float = None
    volt: float = None

    _sqlalchemy_cls = iot.IoTRawData
    _kafka_topic = "data_object.iot_rawdata"


@dataclass
class IoTRawDataCount(DataObject):
    date: date
    device_id: str

    ampere: int = None
    co: int = None
    devstat: int = None
    humidity: int = None
    humidity_main: int = None
    no2: int = None
    noise: int = None
    o3: int = None
    pm1: int = None
    pm2_5: int = None
    pm10: int = None
    temperature: int = None
    temperature_main: int = None
    voc: int = None
    volt: int = None

    _sqlalchemy_cls = iot.IoTRawDataCount
    _kafka_topic = "data_object.iot_rawdata.count"


@dataclass
class IoTEvent(DataObject):
    uid: int = None
    event_id: str = None
    area: str = None
    start_time: datetime = None
    end_time: datetime = None
    duration: int = None
    event_count: int = None
    max_value: float = None
    device_count: int = None
    first_device: str = None
    first_value: float = None
    item: str = None
    score: int = None
    level: int = None
    min_lat: float = None
    min_lon: float = None
    max_lat: float = None
    max_lon: float = None
    device_list: List[Dict[str, Any]] = field(default_factory=list)

    _sqlalchemy_cls = iot.IoTEvent
    _kafka_topic = "data_object.iot_event"


@dataclass
class IoTCircle(DataObject):
    time: datetime = None
    area: str = None
    circle_index: int = None
    score: int = 0
    lat: float = None
    lon: float = None
    radius: float = None

    _sqlalchemy_cls = iot.IoTCircle
    _kafka_topic = "data_object.iot_circle"
