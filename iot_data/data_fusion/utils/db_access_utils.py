# -*- coding: UTF-8 -*-

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from epa.models.sensor_fusion import TaichungPM25
from epa.models import LassRawData, IoTRawData, EpaStationRawData
from utils.preprocessing_utils import standardlized_pm25
from utils.datetime_utils import get_str_datetime_by_current_hour_by_datetime_obj, \
                                    get_str_datetime_by_next_hour_by_datetime_obj


def query_iot_data_with_valid_pm25(fileds=['time',
                                           'device_id',
                                           'lat',
                                           'lon',
                                           'pm2_5'],
                                   where=[]):
    df = IoTRawData.db.read(
        fields=fileds,
        where=where,
        limit=0,
        offset=0,
    ).as_df()

    df = standardlized_pm25(df)

    if not df.empty:
        return df[~(pd.isnull(df.pm2_5))]
    else:
        return None

def query_lass_data_with_valid_pm25(fileds=['time',
                                            'device_id',
                                            'lat',
                                            'lon',
                                            'pm2_5'],
                                    where=[]):
    df = LassRawData.db.read(
        fields=fileds,
        where=where,
        limit=0,
        offset=0,
    ).as_df()

    df = standardlized_pm25(df)

    if not df.empty:
        return df[~(pd.isnull(df.pm2_5))]
    else:
        return None

def query_epa_station_data_with_valid_pm25(fileds=['time',
                                                   'device_id',
                                                   'lat',
                                                   'lon',
                                                   'pm2_5'],
                                           where=[]):
    df = EpaStationRawData.db.read(
        fields=fileds,
        where=where,
        limit=0,
        offset=0,
    ).as_df()

    df = standardlized_pm25(df)

    if not df.empty:
        return df[~(pd.isnull(df.pm2_5))]
    else:
        return None

def sersor_data_with_valid_pm25_in_section_by_specific_hour(_datetime, min_long, max_long, min_lat, max_lat):
    str_datetime_current_hour = get_str_datetime_by_current_hour_by_datetime_obj(_datetime)
    str_datetime_next_hour = get_str_datetime_by_next_hour_by_datetime_obj(_datetime)

    time_condition_1 = 'time>={}'.format(str_datetime_current_hour)
    time_condition_2 = 'time<{}'.format(str_datetime_next_hour)
    location_contition_1 = 'lon>={}'.format(min_long)
    location_contition_2 = 'lon<={}'.format(max_long)
    location_contition_3 = 'lat>={}'.format(min_lat)
    location_contition_4 = 'lat<={}'.format(max_lat)

    where = [time_condition_1,
             time_condition_2,
             location_contition_1,
             location_contition_2,
             location_contition_3,
             location_contition_4]

    epa_station_data = query_epa_station_data_with_valid_pm25(where=where)
    iot_data = query_iot_data＿with_valid_pm25(where=where)
    lass_data = query_lass_data_with_valid_pm25(where=where)


    return epa_station_data, iot_data, lass_data


def sersor_data_in_section_by_overall_time(min_long, max_long, min_lat, max_lat):
    location_contition_1 = 'lon>={}'.format(min_long)
    location_contition_2 = 'lon<={}'.format(max_long)
    location_contition_3 = 'lat>={}'.format(min_lat)
    location_contition_4 = 'lat<={}'.format(max_lat)

    where = [location_contition_1,
             location_contition_2,
             location_contition_3,
             location_contition_4]

    epa_station_data = query_epa_station_data_with_valid_pm25(where=where)
    iot_data = query_iot_data＿with_valid_pm25(where=where)
    lass_data = query_lass_data_with_valid_pm25(where=where)


    return epa_station_data, iot_data, lass_data


def save_fushion_result_to_db(fusion_result):
    writer = TaichungPM25()
    writer.db.write(fusion_result)