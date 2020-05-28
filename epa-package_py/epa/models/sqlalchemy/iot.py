#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.schema import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy import (Column, String, DateTime, Boolean, Integer,
                        JSON, TIMESTAMP, func, text, Date, SmallInteger)
from sqlalchemy.dialects.mysql import DOUBLE

from . import DeclarativeBase, SQLSourceMixin, create_all_tables


Double = DOUBLE(asdecimal=False)


class IoTDevice(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'device.iot'

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
    mac_id = Column(String(31), )
    devstat = Column(String(31), )
    sb_id = Column(String(31), )
    mb_id = Column(String(31), )
    errorcode = Column(String(63), )
    area = Column(String(31), )
    areatype = Column(String(31), )
    sensors = Column(JSON)

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class IoTRawData(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'rawdata.iot'
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

    ampere = Column(Double, )
    co = Column(Double, )
    devstat = Column(Double, )
    humidity = Column(Double, )
    humidity_main = Column(Double, )
    no2 = Column(Double, )
    noise = Column(Double, )
    o3 = Column(Double, )
    pm1 = Column(Double, )
    pm2_5 = Column(Double, )
    pm10 = Column(Double, )
    temperature = Column(Double, )
    temperature_main = Column(Double, )
    voc = Column(Double, )
    volt = Column(Double, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class IoTRawDataCount(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'rawdata.iot.count'
    __table_args__ = (
        PrimaryKeyConstraint("date", "device_id"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    date = Column(Date, )
    device_id = Column(String(15, collation='utf8_bin'), )

    ampere = Column(SmallInteger, )
    co = Column(SmallInteger, )
    devstat = Column(SmallInteger, )
    humidity = Column(SmallInteger, )
    humidity_main = Column(SmallInteger, )
    no2 = Column(SmallInteger, )
    noise = Column(SmallInteger, )
    o3 = Column(SmallInteger, )
    pm1 = Column(SmallInteger, )
    pm2_5 = Column(SmallInteger, )
    pm10 = Column(SmallInteger, )
    temperature = Column(SmallInteger, )
    temperature_main = Column(SmallInteger, )
    voc = Column(SmallInteger, )
    volt = Column(SmallInteger, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class IoTEvent(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'result.iot.event'
    __table_args__ = (
        UniqueConstraint("start_time", "area"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    uid = Column(Integer, autoincrement=True, primary_key=True)
    event_id = Column(String(20, collation="utf8_bin"), index=True)
    area = Column(String(16, collation='utf8_bin'), )
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)
    event_count = Column(Integer)
    max_value = Column(Double, )
    device_count = Column(Integer)
    first_device = Column(String(15), )
    first_value = Column(Double, )
    item = Column(String(15), )
    score = Column(Integer, )
    level = Column(SmallInteger, )
    min_lat = Column(Double, )
    min_lon = Column(Double, )
    max_lat = Column(Double, )
    max_lon = Column(Double, )
    device_list = Column(JSON)

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class IoTCircle(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'result.iot.circle'
    __table_args__ = (
        PrimaryKeyConstraint("time", "area", "circle_index"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    time = Column(DateTime)
    area = Column(String(16, collation='utf8_bin'), )
    circle_index = Column(Integer)
    score = Column(Integer, default=0)
    lat = Column(Double, )
    lon = Column(Double, )
    radius = Column(Double, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


# Keep this at bottom of file to create table automatically
create_all_tables()
