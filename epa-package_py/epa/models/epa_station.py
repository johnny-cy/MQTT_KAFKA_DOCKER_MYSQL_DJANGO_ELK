#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List

from epa.models._data_object import DataObject
from epa.models.sqlalchemy import epa_station


@dataclass
class EpaStationTextarDevice(DataObject):
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
    sub_device_type: str = None
    sensors: List[str] = None

    _sqlalchemy_cls = epa_station.EpaStationTextarDevice
    _kafka_topic = "data_object.epa_station_textar_device"


@dataclass
class EpaStationTextarRawData(DataObject):
    time: datetime
    device_id: str
    name: str
    lat: float
    lon: float

    amb_temp: float = None
    ch4: float = None
    co: float = None
    co2: float = None
    flow: float = None
    nmhc: float = None
    no: float = None
    no2: float = None
    nox: float = None
    o3: float = None
    pm10: float = None
    pm10_test: float = None
    pm2_5: float = None
    pm2_5_ori: float = None
    pm2_5_test: float = None
    pressure: float = None
    ph_cond: float = None
    ph_rain: float = None
    rain_int: float = None
    rainfall: float = None
    rh: float = None
    shelt_temp: float = None
    so2: float = None
    thc: float = None
    uva: float = None
    uvb: float = None
    wd_hr: float = None
    wind_direct: float = None
    wind_speed: float = None
    ws_hr: float = None

    _sqlalchemy_cls = epa_station.EpaStationTextarRawData
    _kafka_topic = "data_object.epa_station_textar_rawdata"


@dataclass
class EpaStationTextarRawDataCount(DataObject):
    date: date
    device_id: str

    amb_temp: int = None
    ch4: int = None
    co: int = None
    co2: int = None
    flow: int = None
    nmhc: int = None
    no: int = None
    no2: int = None
    nox: int = None
    o3: int = None
    pm10: int = None
    pm10_test: int = None
    pm2_5: int = None
    pm2_5_ori: int = None
    pm2_5_test: int = None
    pressure: int = None
    ph_cond: int = None
    ph_rain: int = None
    rain_int: int = None
    rainfall: int = None
    rh: int = None
    shelt_temp: int = None
    so2: int = None
    thc: int = None
    uva: int = None
    uvb: int = None
    wd_hr: int = None
    wind_direct: int = None
    wind_speed: int = None
    ws_hr: int = None

    _sqlalchemy_cls = epa_station.EpaStationTextarRawDataCount
    _kafka_topic = "data_object.epa_station_textar_rawdata.count"


@dataclass
class EpaStationTextarAbnormal(DataObject):
    time: datetime
    station: str = ""
    item: str = ""
    level: str = ""

    _sqlalchemy_cls = epa_station.EpaStationTextarAbnormal
    _kafka_topic = "data_object.epa_station_textar_abnormal"

