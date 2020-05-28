#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import (Column, String, DateTime, Boolean, TIMESTAMP,
                        func, text, Date, SmallInteger, JSON)
from sqlalchemy.dialects.mysql import DOUBLE

from . import DeclarativeBase, SQLSourceMixin, create_all_tables


Double = DOUBLE(asdecimal=False)


class LassDevice(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'device.lass'

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
    sensors = Column(JSON)

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class LassRawData(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'rawdata.lass'
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

    humidity = Column(Double, )
    pm2_5 = Column(Double, )
    pm10 = Column(Double, )
    temperature = Column(Double, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class LassRawDataCount(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'rawdata.lass.count'
    __table_args__ = (
        PrimaryKeyConstraint("date", "device_id"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    date = Column(Date, )
    device_id = Column(String(15, collation='utf8_bin'), )

    humidity = Column(SmallInteger, )
    pm2_5 = Column(SmallInteger, )
    pm10 = Column(SmallInteger, )
    temperature = Column(SmallInteger, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


# Keep this at bottom of file to create table automatically
create_all_tables()
