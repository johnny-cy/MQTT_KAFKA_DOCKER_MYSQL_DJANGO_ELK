# -*- coding: UTF-8 -*-
import pickle

import numpy as np

from utils import geo_utils


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
            with open('save/clf.pickle', 'rb') as f:
                converter = pickle.load(f)
                converted_pm25 = converter.predict(np.array([self._data.pm2_5.mean()]))[0]
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

