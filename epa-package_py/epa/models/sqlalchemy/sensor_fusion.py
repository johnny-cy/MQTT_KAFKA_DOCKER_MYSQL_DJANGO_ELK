#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import (Column, String, DateTime, Boolean, Integer,
                        TIMESTAMP, func, text)
from sqlalchemy.dialects.mysql import DOUBLE

from . import DeclarativeBase, SQLSourceMixin, create_all_tables


Double = DOUBLE(asdecimal=False)


class TaichungPM25(DeclarativeBase, SQLSourceMixin):
    __tablename__ = 'result.pm25_sensor_fusion'
    __table_args__ = (
        PrimaryKeyConstraint("time", "section_index"),
        {
            "mysql_engine": "RocksDB",
        }
    )

    time = Column(DateTime, )
    county = Column(String(63), )
    section_index = Column(Integer, )
    pm25 = Column(Double, )
    min_lon = Column(Double, )
    max_lon = Column(Double, )
    min_lat = Column(Double, )
    max_lat = Column(Double, )

    _created_at = Column(TIMESTAMP(), server_default=func.now())
    _updated_at = Column(TIMESTAMP(), server_default=text(
        "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

# Keep this at bottom of file to create table automatically
create_all_tables()
