#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# MySQL server Info
MYSQL_ADDRESS = "127.0.0.1"
MYSQL_DB = "epa"
MYSQL_USER = "epa"
MYSQL_PASSWORD = "epa"
MYSQL_CONNECTION_DIALECT = (
    f"mysql+mysqldb://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_ADDRESS}/"
    f"{MYSQL_DB}?charset=utf8mb4"
)

SQLALCHEMY_DB_DIALECT = MYSQL_CONNECTION_DIALECT
