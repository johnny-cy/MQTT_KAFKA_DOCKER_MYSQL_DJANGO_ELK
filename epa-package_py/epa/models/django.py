#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine

from ._data_io import DataIOWriteError


try:
    from local_settings import DJANGO_DB_DIALECT
except ModuleNotFoundError:
    MYSQL_ADDRESS = "mysql"
    MYSQL_DB = "django"
    MYSQL_USER = "django"
    MYSQL_PASSWORD = "django"
    MYSQL_CONNECTION_DIALECT = (
        f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_ADDRESS}/"
        f"{MYSQL_DB}?charset=utf8mb4"
    )
    DJANGO_DB_DIALECT = MYSQL_CONNECTION_DIALECT


djangoEngine = create_engine(DJANGO_DB_DIALECT, encoding='utf8', pool_pre_ping=True, echo=False)


class Notification:
    
    @staticmethod
    def __get_all():
        conn = djangoEngine.connect()
        res = []
        try:
            result = conn.execute("SELECT * FROM feature_configs_notification")
            res = [dict(r) for r in result.fetchall()]
        except Exception as err:
            raise DataIOWriteError(err)
        finally:
            conn.close()
        return res

    @classmethod
    def get_email_list(cls):
        all_data = cls.__get_all()
        return [d['email'] for d in all_data if 'email' in d]

    @classmethod
    def get_email_receiver(cls):
        all_data = cls.__get_all()
        return [EmailReceiver.from_dict(d) for d in all_data if 'email' in d]


class EmailReceiver(object):

    def __init__(self, email, risks, areas):
        self.email = email
        self.risks = list(map(str.strip, risks.split(","))) if risks else []
        self.areas = list(map(str.strip, areas.split(","))) if areas else []

    @classmethod
    def from_dict(cls, data):
        return cls(data["email"], data["risks"], data["area"])

