#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import epa.logging

from . import Handler


logger = epa.logging.get_logger(__name__)


class HTTPHandler(Handler):
    """
    Todos
    -----
    """

    def __init__(self, url="", headers={}, params={}):
        self.url = url
        self.headers = headers
        self.params = params
        self.pre_read_func = None
        self.post_read_func = None
        self.url_delegate = None

    def read(self):
        for url, headers, params in self._url_generator():
            if self.pre_read_func:
                self.pre_read_func()

            headers.update({"ck": self.project.api_key})
            ret = self._send_request(url, headers, params)
            if isinstance(ret, (list, tuple)):
                yield from ret
            else:
                yield ret

            if self.post_read_func:
                self.post_read_func()

    def _url_generator(self):
        if self.url_delegate:
            yield from self.url_delegate()
        else:
            while True:
                yield self.url, self.headers, self.params

    def _send_request(self, url, headers={}, params={}):
        logger.debug(f"_send_request: {url}, {headers}, {params}")
        try:
            res = requests.get(url, headers=headers, params=params,
                               timeout=600)
            if res.ok:
                return res.json()
            else:
                logger.error(f"Return {{}} because HTTP error: "
                             f"{res.reason} [{url}, {headers}, {params}]")
                return {}
        except requests.Timeout:
            logger.error(f"Return {{}} because HTTP timeout "
                         f"[{url}, {headers}, {params}]")
            return {}

    def close(self):
        pass


class DeviceHTTPHandler(HTTPHandler):
    device_url = "https://iot.epa.gov.tw/iot/v1/device"

    def __init__(self):
        super().__init__(DeviceHTTPHandler.device_url)
        self._project = None

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value
        self.headers = {"ck": self.project.api_key}

    def read(self):
        device_map = self.project.device_map
        for device in super().read():
            device["sensors"] = list(device_map[device["id"]].sensors)
            yield device

