# -*- coding: UTF-8 -*-
import time
from argparse import ArgumentParser
from datetime import datetime, date, timedelta
import pickle

import pandas as pd
import numpy as np
# import cv2


from utils import geo_utils, db_access_utils, datetime_utils, preprocessing_utils



class PM25Handler:

    def __init__(self):
        raise NotImplementedError

    @property
    def next(self):
        return next

    @next.setter
    def next(self, chain_element):
        self._next = chain_element

    def calculate_pm25(self):
        if self._data is not None:
            return self._data.pm2_5.mean()

        else:
            return self._next.calculate_pm25()


class EpaPM25Handler(PM25Handler):
    def __init__(self, data):
        self._data = data


class IotPM25Handler(PM25Handler):
    def __init__(self, data):
        self._data = data


class LassPM25Handler(PM25Handler):
    def __init__(self, data):
        self._data = data

    def calculate_pm25(self):
        if self._data is not None:
            with open('models/2018-08-24_svr_rmse_7.05.pickle', 'rb') as f:
                converter = pickle.load(f)
                converted_pm25 = converter.predict(np.array([self._data.pm2_5.mean()]).reshape((-1, 1)))[0]

            f.close()

            return converted_pm25

        else:
            return np.nan



def calculate_pm25_in_section(epa_data, iot_data, lass_data, min_max_lon, min_max_lat):
    min_lon, max_lon = min_max_lon
    min_lat, max_lat = min_max_lat

    epa_data_in_section, iot_data_in_section,lass_data_in_section = None, None, None

    if epa_data is not None:
        epa_data_in_section = geo_utils.get_device_data_in_section(epa_data, min_lon, max_lon, min_lat, max_lat)
    if iot_data is not None:
        iot_data_in_section = geo_utils.get_device_data_in_section(iot_data, min_lon, max_lon, min_lat, max_lat)
    if lass_data is not None:
        lass_data_in_section = geo_utils.get_device_data_in_section(lass_data, min_lon, max_lon, min_lat, max_lat)

    pm25_chain_head = EpaPM25Handler(epa_data_in_section)
    pm25_chain_mid = IotPM25Handler(iot_data_in_section)
    pm25_chain_end = LassPM25Handler(lass_data_in_section)

    pm25_chain_head.next = pm25_chain_mid
    pm25_chain_mid.next = pm25_chain_end

    return pm25_chain_head.calculate_pm25()


def pm25_diff_in_section(epa_data, iot_data, lass_data, min_max_lon, min_max_lat):
    min_lon, max_lon = min_max_lon
    min_lat, max_lat = min_max_lat

    epa_data_in_section, iot_data_in_section,lass_data_in_section = None, None, None

    if epa_data is not None:
        epa_data_in_section = geo_utils.get_device_data_in_section(epa_data, min_lon, max_lon, min_lat, max_lat)
    if iot_data is not None:
        iot_data_in_section = geo_utils.get_device_data_in_section(iot_data, min_lon, max_lon, min_lat, max_lat)
    if lass_data is not None:
        lass_data_in_section = geo_utils.get_device_data_in_section(lass_data, min_lon, max_lon, min_lat, max_lat)

    pm25_chain_head = EpaPM25Handler(epa_data_in_section)
    pm25_chain_mid = IotPM25Handler(iot_data_in_section)
    pm25_chain_end = LassPM25Handler(lass_data_in_section)

    pm25_chain_head.next = pm25_chain_mid
    pm25_chain_mid.next = pm25_chain_end

    return pm25_chain_head.calculate_pm25()



def pm25_distribution(county, _datetime):
    map_sections = geo_utils.MapBuilder.build_map_sections(county.min_long,
                                                              county.max_long,
                                                              county.min_lat,
                                                              county.max_lat)

    station_data, iot_data, lass_data = db_access_utils.sersor_data_with_valid_pm25_in_section_by_specific_hour(_datetime,
                                                                                                                county.min_long,
                                                                                                               county.max_long,
                                                                                                               county.min_lat,
                                                                                                               county.max_lat)


    fusion_result = []

    for i, (min_lon, min_lat, max_lon, max_lat) in enumerate(map_sections):
        pm25 = calculate_pm25_in_section(station_data, iot_data, lass_data,
                                         (min_lon, max_lon), (min_lat, max_lat))


        fusion_result.append([_datetime,
                              county.name,
                              datetime.now(),
                              i,
                              pm25,
                              min_lon,
                              max_lon,
                              min_lat,
                              max_lat
                              ])

    fusion_result = pd.DataFrame(fusion_result, columns=['time',
                                                         'county',
                                                         '_created_at',
                                                         'section_index',
                                                         'pm25',
                                                         'min_lon',
                                                         'max_lon',
                                                         'min_lat',
                                                         'max_lat'
                                                         ])
    return  fusion_result


def do_data_fusion_and_save(county, _datetime, output_filename=None):
    raw_pm25_heatmap = pm25_distribution(county=county, _datetime=_datetime)
    raw_pm25_heatmap.pm25 = preprocessing_utils.interpolate(raw_pm25_heatmap.pm25.values)
    raw_pm25_heatmap = raw_pm25_heatmap.dropna()
    print(raw_pm25_heatmap.shape)
    db_access_utils.save_fushion_result_to_db(raw_pm25_heatmap)

    if output_filename:
        raw_pm25_heatmap.to_csv('{}.csv'.format(output_filename))


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


if __name__ == '__main__':

    arg_parser = ArgumentParser()
    arg_parser.add_argument('-c', '--county', required=True)
    arg_parser.add_argument('-d', '--datetime', required=True)
    arg_parser.add_argument('-d2', '--datetime_2', required=False)
    arg_parser.add_argument('-o', '--output_filename', required=False)
    args = vars(arg_parser.parse_args())

    county = args['county']

    _datetime = args['datetime']
    _datetime = datetime.strptime(_datetime, "%Y-%m-%d %H:%M:%S")
    _datetime = _datetime.replace(minute=0, second=0)

    _datetime_2 = args['datetime_2']
    if _datetime_2 is not None:
        _datetime_2 = datetime.strptime(_datetime_2, "%Y-%m-%d %H:%M:%S")
        _datetime_2 = _datetime_2.replace(minute=0, second=0)

    output_filename = args['output_filename']

    assert county is not None, "Please select a valid county."
    assert _datetime is not None, "Specify datetime to run date fusion."

    if _datetime_2 is None:
        do_data_fusion_and_save(county=geo_utils.get_county_geo_info(county),
                                _datetime=_datetime,
                                output_filename=output_filename)
    else:
        start_date = date(_datetime.year, _datetime.month, _datetime.day)
        end_date = date(_datetime_2.year, _datetime_2.month, _datetime_2.day)
        for single_date in daterange(start_date, end_date):
            # print(single_date)
            for hour in range(24):

                current_datetime = datetime(single_date.year, single_date.month, single_date.day, hour)


                do_data_fusion_and_save(county=geo_utils.get_county_geo_info(county),
                                        _datetime=current_datetime,
                                        output_filename=output_filename)
