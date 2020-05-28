#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.parse
import datetime

import dateutil.parser
from epa.area import all_areas
from epa.logging import get_logger

from main import main_func
from coordinator import Coordinator
from etl_functions import ETLMixin

#all_areas += ["斗六工業區","西螺果菜市場","元長工業區","豐田工業區","斗六聯絡道路"]
logger = get_logger(__name__)

HTTP_HOST = os.environ.get("HTTP_HOST",
        default="analysis.epa.gov.tw")
ANIMATION_URL = os.environ.get("ANIMATION_URL",
        default="web/iot/history/animation")


def generate_url(start, end, area_name):
    area = None
    for a in all_areas:
        if area_name == a.name:
            area = a
            break
    if not area:
        logger.warning(f"Area not found: {area_name}")
        return None

    params = {
        "start": start,
        "end": end,
        "start_lon": area.min_lon,
        "end_lon": area.max_lon,
        "start_lat": area.min_lat,
        "end_lat": area.max_lat,
    }
    url_params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    ret = f"https://{HTTP_HOST}/{ANIMATION_URL}?{url_params}"
    return ret


class EventTransmitter(Coordinator, ETLMixin):

    def reset(self):
        super().reset()

        self.areas = self.config.areas
        self._10_min_queue = {}

    def post_read(self, data):
        def _d_info(d):
            return {
                "deviceId": d["device_id"],
                "name": d["name"],
                "maxValue": int(max(filter(None, d["pm2_5"]))),
            }
        data["device_list"] = [_d_info(d) for d in data["device_list"]]
        data["pid"] = self.config.project.code
        data["url"] = generate_url(data["start_time"], data["end_time"], data["area"])

        if data["area"] not in self.areas:
            yield from []
        elif not self._is_event_happening(data) or \
             not self._is_queue_10_minutes(data):
            yield from []
        else:
            yield from self.etl_value(data)

    def _is_event_happening(self, data):
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=10)
        ret = (now - dateutil.parser.parse(data["end_time"])) < delta
        #logger.info(f"is event happening? {ret}")
        return ret

    def _is_queue_10_minutes(self, data):
        now = datetime.datetime.now()

        ret = False
        key = (data["area"], data["start_time"])
        try:
            last_sent_time = self._10_min_queue[key]
            if now - last_sent_time > datetime.timedelta(minutes=10):
                self._10_min_queue[key] = now
                ret = True
        except KeyError:
            self._10_min_queue[key] = now
            ret = True

        #logger.info(f"is queue 10 minutes? {ret}")
        return ret


def main():
    main_func(EventTransmitter,
              process_name="mqtt_transmitter",
              description="Transmit MQTT data",
              )


if __name__ == "__main__":
    main()


