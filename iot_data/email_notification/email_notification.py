#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import smtplib
import urllib.parse
import datetime

import jinja2
import yaml
import dateutil.parser

from epa.models import IoTEvent
from epa.area import (TaichungPort, TaichungIndustry, Guanyin,
                      Houli, Dajia,
                      Tucheng,
                      Yilan,
                      Dayuan, Guishan, Hwaya, Longtan,
                      HsinchuIndustry, HsinchuSciencePark, HsinchuCity,
                      Toufen, MiaoliCity,
                      YunlinIndustryPark, YunlinIndustryJhuweizih,
                      ChiayiCity, Minxiong,
                      Jiali, Rende, Baoan,
                      Linyuan, Dafa, Linhai, KaohsiungCity, Jenwu,
                      PingnanIndustry, PingnanExportProcessingZone,
                      Neipu, PingtungCity, AgriculturalBiotechnologyPark,
                      Changhua,
                      Keelung,
                      ChuansingIndustrialPark,
                      ChanghuaCoastalIndustrialPark,
                      FangyuanIndustrialPark,
                      TapurunIndustrialPark,
                      )
from epa.logging import get_logger
from epa.models.django import Notification

logger = get_logger(__name__)
gmail_user = "analysis.cameo@epa.gov.tw"
gmail_password = ""

HTTP_HOST = os.environ.get("HTTP_HOST",
        default="analysis.epa.gov.tw")
ANIMATION_URL = os.environ.get("ANIMATION_URL",
        default="web/iot/history/animation")
SMTP_SERVER = "a0-smtp.epa.gov.tw"
SMTP_PORT = 25

Areas = (TaichungPort, TaichungIndustry, Guanyin,
         Houli, Dajia,
         Tucheng,
         Yilan,
         Dayuan, Guishan, Hwaya, Longtan,
         HsinchuIndustry, HsinchuSciencePark, HsinchuCity,
         Toufen, MiaoliCity,
         YunlinIndustryPark, YunlinIndustryJhuweizih,
         ChiayiCity, Minxiong,
         Jiali, Rende, Baoan,
         Linyuan, Dafa, Linhai, KaohsiungCity, Jenwu,
         PingnanIndustry, PingnanExportProcessingZone,
         Neipu, PingtungCity, AgriculturalBiotechnologyPark,
         )


class SMTPClient(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def send_email(self, recipient, subject, body, contentType='text/html'):
        FROM = str(self.user)
        TO = recipient if type(recipient) is list else [recipient]
        SUBJECT = str(subject)
        TEXT = str(body)

        # Prepare actual message
        message = """From: %s\nTo: %s\nContent-Type: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), contentType, SUBJECT, TEXT)

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.ehlo()
            # server.starttls()
            # server.login(self.user, self.password)
            server.sendmail(FROM, TO, message.encode('utf-8'))
            # server.close()
            logger.info(f"successfully sent the mail, {SUBJECT}, to {TO}")
        except BaseException as e:
            logger.exception("run exception : {}".format(e))
            logger.error("failed to send mail")


class FilterMidLevel(object):
    def __call__(self, events):
        return [e for e in events
                if e["event_count"] >= 10 and e["duration"] >= 10]


class Filter10MinuteQueue(object):

    def __init__(self):
        # using (area, start_time) as key, last email sent time as value
        self.map = {}

    def __call__(self, events):
        now = datetime.datetime.now()

        ret = []
        for event in events:
            key = (event["area"], event["start_time"])
            try:
                last_sent_time = self.map[key]
                if now - last_sent_time > datetime.timedelta(minutes=10):
                    ret.append(event)
                    self.map[key] = now
            except KeyError:
                ret.append(event)
                self.map[key] = now

        return ret


class FilterHappening(object):

    def __call__(self, events):
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=10)

        return [e for e in events if now - dateutil.parser.parse(e["end_time"]) < delta]

class FilterLoadUID(object):
    
    def __call__(self, events):
        for event in events:
            e = IoTEvent.db.read(
                    fields=["uid"],
                    where=[
                        "start_time = :start_time",
                        "area = :area",
                    ],
                    start_time = event["start_time"],
                    area = event["area"],
                    ).get_one()
            if e:
                event["uid"] = e["uid"]
        return events



class EventNotifier(object):
    def __init__(self):
        self.smtp = SMTPClient(gmail_user, gmail_password)
        self.filters = [
            FilterHappening(),
            # FilterMidLevel(),
            Filter10MinuteQueue(),
            FilterLoadUID(),
        ]

        self.load_template()

    def load_email_list(self):
        self.email_receivers = Notification.get_email_receiver()

    def check_email_receiver(self, event):
        area = event["area"]
        duration = event["duration"]
        event_count = event["event_count"]
        risk = "高" if duration > 15 and event_count > 15 else \
               "中" if duration > 10 and event_count > 10 else \
               "低"

        def _check_risks(receiver):
            return True if risk in receiver.risks or \
                           len(receiver.risks) == 0 else False

        def _check_areas(receiver):
            return True if area in receiver.areas or \
                           len(receiver.areas) == 0 else False

        def _check(receiver):
            return _check_risks(receiver) and _check_areas(receiver)

        return [r.email for r in self.email_receivers if _check(r)]


    def load_template(self):
        with open('event.html') as f:
            self.body_template = jinja2.Template(f.read())
        self.subject_template = jinja2.Template(
            "[污染推播 {{ risk }}風險 #{{ uid }}] {{ area }} {{ start_time }} 時發生歷時 "
            "{{ duration }}分鐘事件 - 最高 iot 數值: {{ max_value }}")

    def listen(self):
        for events in IoTEvent.kafka.read().as_stream():
            events = events.as_list()
            logger.debug(f"  Received event length: {len(events)}")
            if not events:
                continue

            for f in self.filters:
                events = f(events)
                if not events:
                    break
            if not events:
                continue

            self.load_email_list()

            for event in events:
                event["url"] = generate_url(event["start_time"],
                                            event["end_time"], event["area"])
                duration = event["duration"]
                event_count = event["event_count"]
                risk = "高" if duration > 15 and event_count > 15 else \
                       "中" if duration > 10 and event_count > 10 else \
                       "低"
                event["risk"] = risk
                subject = self.subject_template.render(event)
                body = self.body_template.render(event)

                recipient = self.check_email_receiver(event)
                self.smtp.send_email(recipient, subject, body)


def generate_url(start, end, area_name):
    area = None
    for a in Areas:
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


def main():
    event_notifier = EventNotifier()
    event_notifier.listen()


if __name__ == "__main__":
    main()
