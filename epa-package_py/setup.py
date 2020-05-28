#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup


setup(
    name="epa",
    version="0.1",
    description="Cameo EPA package",
    author="YiKai Lin",
    author_email="yikai@cameo.tw",
    packages=[
        "epa",
        "epa.models",
        "epa.models.kafka",
        "epa.models.sqlalchemy",
    ],
    install_requires=[
        "confluent-kafka>=0.11.5",
        "mysqlclient>=1.3.12",
        "SQLAlchemy>=1.2.8",
        "pandas>=0.23.1",
        "dataclasses; python_version < '3.7'",
    ],
)
