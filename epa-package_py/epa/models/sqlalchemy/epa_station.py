#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import (Column, String, DateTime, Boolean, TIMESTAMP,
                        func, text, Date, SmallInteger, JSON)
from sqlalchemy.dialects.mysql import DOUBLE

from . import DeclarativeBase, SQLSourceMixin, create_all_tables


Double = DOUBLE(asdecimal=False)


class EpaStationTextarDevice(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'device.epa_station.textar'

    device_id = Column(String(15), primary_key=True)
    name = Column(String(63), )
    desc = Column(String(127), )
    type = Column(String(31), )
    lat = Column(Double, )
    lon = Column(Double, )
    alt = Column(Double, )
    reference = Column(Boolean, )
    display = Column(Boolean, )
    device_type = Column(String(15), )
    owner_id = Column(String(31), )
    mobile = Column(Boolean, )
    outdoor = Column(Boolean, )
    manufacturer_id = Column(String(31), )
    sub_device_type = Column(String(31), )
    sensors = Column(JSON)

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class EpaStationTextarRawData(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'rawdata.epa_station.textar'
    __table_args__ = (
        PrimaryKeyConstraint("time", "device_id"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    time = Column(DateTime, )
    device_id = Column(String(15, collation='utf8_bin'), )
    name = Column(String(63), )
    lat = Column(Double, )
    lon = Column(Double, )

    amb_temp = Column(Double, )
    ch4 = Column(Double, )
    co = Column(Double, )
    co2 = Column(Double, )
    flow = Column(Double, )
    nmhc = Column(Double, )
    no = Column(Double, )
    no2 = Column(Double, )
    nox = Column(Double, )
    o3 = Column(Double, )
    pm10 = Column(Double, )
    pm10_test = Column(Double, )
    pm2_5 = Column(Double, )
    pm2_5_ori = Column(Double, )
    pm2_5_test = Column(Double, )
    pressure = Column(Double, )
    ph_cond = Column(Double, )
    ph_rain = Column(Double, )
    rain_int = Column(Double, )
    rainfall = Column(Double, )
    rh = Column(Double, )
    shelt_temp = Column(Double, )
    so2 = Column(Double, )
    thc = Column(Double, )
    uva = Column(Double, )
    uvb = Column(Double, )
    wd_hr = Column(Double, )
    wind_direct = Column(Double, )
    wind_speed = Column(Double, )
    ws_hr = Column(Double, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class EpaStationTextarRawDataCount(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'rawdata.epa_station.textar.count'
    __table_args__ = (
        PrimaryKeyConstraint("date", "device_id"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    date = Column(Date, )
    device_id = Column(String(15, collation='utf8_bin'), )

    amb_temp = Column(SmallInteger, )
    ch4 = Column(SmallInteger, )
    co = Column(SmallInteger, )
    co2 = Column(SmallInteger, )
    flow = Column(SmallInteger, )
    nmhc = Column(SmallInteger, )
    no = Column(SmallInteger, )
    no2 = Column(SmallInteger, )
    nox = Column(SmallInteger, )
    o3 = Column(SmallInteger, )
    pm10 = Column(SmallInteger, )
    pm10_test = Column(SmallInteger, )
    pm2_5 = Column(SmallInteger, )
    pm2_5_ori = Column(SmallInteger, )
    pm2_5_test = Column(SmallInteger, )
    pressure = Column(SmallInteger, )
    ph_cond = Column(SmallInteger, )
    ph_rain = Column(SmallInteger, )
    rain_int = Column(SmallInteger, )
    rainfall = Column(SmallInteger, )
    rh = Column(SmallInteger, )
    shelt_temp = Column(SmallInteger, )
    so2 = Column(SmallInteger, )
    thc = Column(SmallInteger, )
    uva = Column(SmallInteger, )
    uvb = Column(SmallInteger, )
    wd_hr = Column(SmallInteger, )
    wind_direct = Column(SmallInteger, )
    wind_speed = Column(SmallInteger, )
    ws_hr = Column(SmallInteger, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


EpaStationRawData = EpaStationTextarRawData
EpaStationDevice = EpaStationTextarDevice


class EpaStationTextarAbnormal(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'result.epa_station.abnormal.textar'
    __table_args__ = (
        PrimaryKeyConstraint("time", "station", "item"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    time = Column(DateTime, )
    station = Column(String(15, collation='utf8_bin'), )
    item = Column(String(15), )
    level = Column(String(15), )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


# Keep this at bottom of file to create table automatically
create_all_tables()
