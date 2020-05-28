#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import itertools
from datetime import datetime, timedelta

import pytz
import numpy as np
import pandas as pd
from epa.utils import get_class_with_name
import epa.logging


logger = epa.logging.get_logger(__name__)


class ETLMixin(object):

    def etl_value(self, value):
        print("print out etl_value")
        print(type(value))
        print(value)
        try:
            for etl in self.etl:
                func_name, kwargs = list(etl.items())[0]
                value = globals()[func_name](value, **kwargs)
            if value is not None:
                yield value
            else:
                yield from []
        except Exception as e:
            logger.exception(f"ETL error: {e} args: {value}")
            yield from []


def take_first(value, field):
    """ Take first element of list. """
    try:
        value[field] = value[field][0]
    except IndexError:
        value[field] = None
    return value


def update_from_dict_list(value, field, drop=True):
    """ Update value from dict list contains {"key": x, "value": y}. """
    try:
        value.update({x["key"]: x["value"] for x in value[field]})
        if drop:
            del value[field]
    except KeyError:
        pass
    return value


def replace_value(value, field, old_values=[], new_value=None):
    """ Replace field's value if value euqal one of old_values"""
    try:
        if value[field] in old_values:
            value[field] = new_value
    except KeyError:
        pass
    return value


def rename(value, fields={}):
    """ Rename fields. """
    for k, v in fields.items():
        try:
            value[v] = value.pop(k)
        except KeyError:
            continue
    return value


def rename_from_field_value(value, field, from_field, drop=True):
    """ Rename a field with value form another field's value. """
    try:
        new_name = value[from_field]
        value[new_name] = value.pop(field)
        if drop:
            del value[from_field]
    except KeyError:
        pass
    return value


def drop(value, fields=[]):
    """ Drop fields. """
    for f in fields:
        try:
            del value[f]
        except KeyError:
            continue
    return value


def select(value, fields=[]):
    """ Select fields. """
    return {f: value[f] for f in fields if f in value}


def to_numeric(value, fields=[], numeric_type="float"):
    """ Convert field's value to numeric. """
    convert_func = int if numeric_type == "int" else float
    for f in fields:
        try:
            value[f] = convert_func(value[f])
        except (ValueError, KeyError):
            continue
        except TypeError:
            if value[f] is None:
                value[f] = None
            else:
                raise
    return value


def to_bool(value, fields=[]):
    """ Convert string "True"/"False" to bool. """
    for f in fields:
        try:
            str_value = str(value[f]).lower()
            value[f] = True if str_value == "true" else \
                       False if str_value == "false" else \
                       value[f]
        except KeyError:
            continue
    return value


def to_str(value, fields=[]):
    """ Convert string "True"/"False" to string. """
    for f in fields:
        try:
            value[f] = str(value[f])
        except KeyError:
            continue
    return value


device_map = {}
device_map_load_time = {}

def append_device_name_lat_lon(value, device_cls_name):
    """ Append device's name/lat/lon """
    try:
        load_time = device_map_load_time[device_cls_name]
        if datetime.now() - load_time > timedelta(hours=24):
            del device_map[device_cls_name]
        df_device = device_map[device_cls_name]
    except KeyError:
        device_cls = get_class_with_name("epa.models", device_cls_name)
        fields = ["device_id", "name", "lat", "lon"]
        df_device = device_cls.db.read(fields=fields).as_df()
        logger.info(f"Load device_cls: {device_cls_name}, "
                    f" length: {len(df_device)}")
        if not df_device.empty:
            df_device = df_device.set_index("device_id")
            df_device = df_device[df_device["lat"].notna() & \
                                  df_device["lon"].notna()]
            df_device = df_device.where(pd.notnull(df_device), None)
        else:
            df_device = None
        device_map[device_cls_name] = df_device
        device_map_load_time[device_cls_name] = datetime.now()

    if df_device is None:
        return value

    if "name" not in value or \
       "lat" not in value or \
       "lon" not in value:
        try:
            device_info = df_device.loc[value["device_id"]].to_dict()
            value.update(device_info)
        except KeyError:
            pass

    return value


def datetime_to_isoformat(value, field, parsing_format, zoneinfo=None):
    """ Convert datetime string to ISO format. """
    t = datetime.strptime(value[field], parsing_format)
    if zoneinfo:
        t = pytz.timezone(zoneinfo).localize(t)
    try:
        value[field] = t.isoformat()
    except KeyError:
        pass
    return value


def compose(value, new_field, from_fields, drop=True, skip_no_value=True):
    """ Compose new field from self value. """
    try:
        new_value = {f: value[f] for f in from_fields if f in value}
        if new_value or not skip_no_value:
            value[new_field] = new_value
            if drop:
                for f in from_fields:
                    del value[f]
    except KeyError:
        pass
    return value


def blacklist(value, key, ignore_list):
    if value[key] in ignore_list:
        return None
    else:
        return value

