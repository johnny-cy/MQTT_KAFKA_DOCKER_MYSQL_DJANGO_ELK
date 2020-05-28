#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
from datetime import datetime

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import epa.logging


# Eliminate warnning message from requests when verify=False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = epa.logging.get_logger(__name__)

MAX_RESULT_SIZE_HARD_LIMIT = 10000


class JSONResultTruncatedException(Exception):
    """Fetched result is truncated"""

    def __init__(self, result):
        self.result_length = len(result)


class IoTServerError(Exception):
    """ Temporary banned by server """


def get_json_result(url, api_key, retry=10):
    i = 1
    while i <= retry:
        try:
            return _get_json_result(url, api_key)
        except IoTServerError:
            logger.warning(f"Banned by server, sleep {2**i} seconds ...")
            time.sleep(2**i)
            i += 1
    logger.error("Exceed retry {retry} times, return emtpy result")
    return []


def _get_json_result(url, api_key):
    headers = {"ck": api_key}
    response = requests.get(url, headers=headers, verify=False)
    try:
        result = response.json()
    except Exception as e:
        logger.exception(e)
        logger.error(f"requests for {url} error, return empty result - []")
        return []
    if len(result) >= MAX_RESULT_SIZE_HARD_LIMIT:
        logger.debug(f"  Result truncated, result size: {len(result)}")
        raise JSONResultTruncatedException(result)
    return result


class IoTProject(object):
    device_url = "https://iot.epa.gov.tw/iot/v1/device"
    latest_sensor_rawdata = ("https://iot.epa.gov.tw/iot/v1/sensor/"
                             "{sensor_id}/rawdata")
    rawdata_count_url = ("https://iot.epa.gov.tw/iot/v1/count/project"
                         "/{project_id}/sensor/{sensor_id}?start={start}&end={end}")

    def __init__(self, code, name, api_key, devices=set(), sensors=set()):
        self.code = code
        self.name = name
        self.api_key = api_key
        self._sensors = sensors
        self._device_map = {d: self.gen_device(d) for d in devices}
        self._raw_devices = None

    def __repr__(self):
        return f"{self.code} - {self.name}"

    @property
    def device_map(self):
        if not self._device_map:
            self._device_map = {x["id"]: self.gen_device(x["id"])
                                for x in self.raw_devices}
            logger.debug(f"  IoTProject._device_map is empty, updated -> "
                         f"{self._device_map}")
        return self._device_map

    @property
    def devices(self):
        return set(self.device_map.values())

    @property
    def raw_devices(self):
        if not self._raw_devices:
            self._raw_devices = get_json_result(self.device_url, self.api_key)
            logger.debug(f"  IoTProject._raw_devices is empty, updated "
                         f"length -> {len(self._raw_devices)}")
        return self._raw_devices

    def gen_device(self, device_id):
        return IoTDevice(self, device_id, self._sensors)

    @property
    def sensors(self):
        """Cumulated sensors of devcies"""
        if not self._sensors:
            self._sensors = set()
            k = min(len(self.devices), 20)
            for device in random.sample(self.devices, k=k):
                self._sensors.update(device.sensors)
            logger.debug(f"  IoTProject._sensors is empty, updated -> "
                         f"{self._sensors}")
        return self._sensors

    def fetch_rawdata(self, start, end, sensors=set()):
        for device in self.devices:
            yield from device.fetch_rawdata(start, end, sensors)

    def fetch_latest_rawdata(self, sensors=set()):
        sensors = sensors or self.sensors
        for sensor in sensors:
            logger.debug(f"  fetching latest rawdata: {self.code} {sensor}")
            url = self.latest_sensor_rawdata.format(sensor_id=sensor)
            result = get_json_result(url, self.api_key)
            yield from result

    def update_sensor_counts(self, sensor_id: str, start: datetime, end: datetime) -> None:
        """ Update rawdata count for sensor_id

        This function will update rawdata count for project internal devices.

        Args:
            sensor_id: sensor_id to update
            start: start time
            end: end time

        Returns:
            None
        """

        url = self.rawdata_count_url.format(project_id=self.code,
                                            sensor_id=sensor_id, start=start, end=end)
        result = get_json_result(url, self.api_key)
        key = (sensor_id, start, end)
        for device_id, count in result["deviceCountMap"].items():
            try:
                device = self._device_map[device_id]
                device.update_rawdata_count(key, count)
            except KeyError:
                pass


class IoTDevice(object):
    sensor_url = "https://iot.epa.gov.tw/iot/v1/device/{device_id}/sensor"
    rawdata_url = ("https://iot.epa.gov.tw/iot/v1/device/{device_id}"
                   "/sensor/{sensor_id}/rawdata"
                   "?start={start:%Y-%m-%d %H:%M:%S}"
                   "&end={end:%Y-%m-%d %H:%M:%S}")

    def __init__(self, project: IoTProject, device_id: str, sensors: set=set()):
        """
        Args:
            project: This device belongs to.
            device_id: Device ID string name.
            sensors: Set of sensors included in this device.
        """
        self.project = project
        self.api_key = self.project.api_key
        self.device_id = device_id
        self._sensors = sensors
        self._rawdata_counts = {}

    def __hash__(self):
        return int(self.device_id)

    def __repr__(self):
        return f"{self.device_id}"

    @property
    def sensors(self):
        if not self._sensors:
            url = self.sensor_url.format(device_id=self.device_id)
            result = get_json_result(url, self.api_key)
            self._sensors = {x["id"] for x in result}
            logger.debug(f"  IoTDevice._sensors is empty, updated -> "
                         f"{self._sensors}")
        return self._sensors

    def get_rawdata_count(self, sensor_id: str, start: datetime, end: datetime) -> int:
        """ Get rawdata count for sensor_id in this device

        Args:
            sensor_id: sensor_id
            start: start time
            end: end time

        Returns:
            int: count number for sensor `sensor_id`
        """
        if sensor_id not in self._sensors:
            logger.warning(f"Sensor ID \"{sensor_id}\" not in device "
                           f"{self.device.id}.")
            return 0

        key = (start, end)
        try:
            return self._rawdata_counts[key]
        except KeyError:
            self.project.update_sensor_count(sensor_id, start, end)
            return self.get_rawdata_count(sensor_id, start, end)

    def fetch_rawdata(self, start, end, sensors=set()):
        sensors = sensors or self.sensors
        for sensor in sensors:
            yield from self.fetch_sensor_rawdata(sensor, start, end)

    def fetch_sensor_rawdata(self, sensor_id, start, end):
        logger.debug(f"  fetching rawdata: {self.device_id} {sensor_id} "
                     f"{start} - {end}")
        url = self.rawdata_url.format(device_id=self.device_id,
                                      sensor_id=sensor_id,
                                      start=start,
                                      end=end)
        result = get_json_result(url, self.api_key)
        yield from result

    def check_integrity(self, sensor_id: str, start: datetime, end: datetime,
                        retry_update: bool=True):
        """ Compare data count from server with data count in DB

        Args:
            sensor_id: sensor ID
            start: start time
            end: end time
            retry_update:

        Returns:
            bool: `True` if both counts are the same, `False` if not equal
        """
        key = (sensor_id, start, end)
        try:
            count = self._rawdata_counts[key]
            data_cls = self.project.data_cls
            if not hasattr(data_cls, sensor_id):
                return False
            result = data_cls.db.read(fields=[sensor_id], where=[
                "time >= :start",
                "time < :end",
            ], start=start, end=end).as_list()
            return len(result) == count
        except KeyError:
            if retry_update:
                self.project.update_sensor_counts(sensor_id, start, end)
                return self.check_integrity(sensor_id, start, end, False)
            else:
                return False

    def update_rawdata_count(self, key, value):
        self._rawdata_counts[key] = value
