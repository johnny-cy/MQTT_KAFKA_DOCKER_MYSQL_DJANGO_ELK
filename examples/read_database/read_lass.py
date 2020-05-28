#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

from epa.models import LassRawData


def read_examples():
    print("Fetch all data for LassRawData")
    df = LassRawData.read_df()
    print(df)
    print()

    print("Fetch all data for LassRawData, but only specified columns")
    df = LassRawData.read_df(columns=["time", "device_id"])
    print(df)
    print()

    print("Filtering with where")
    df = LassRawData.read_df(where=["device_id = '1530068615'"])
    print(df)
    print()

    print("Multiple where statement with list, these statement are ANDed")
    where = [
        "time > '2018-05-01'",  # Not good to embeded variable in statement
        "time < '2018-05-08'",
    ]
    df = LassRawData.read_df(where=where)
    print(df)
    print()

    print("Statement with variables")
    start_time = datetime.date(2018, 5, 1)
    end_time = datetime.date(2018, 5, 8)
    where = [
        "time > :start_time",   # variable format ":var_name"
        "time < :end_time",
    ]
    df = LassRawData.read_df(where=where,
                             start_time=start_time, end_time=end_time)
    print(df)
    print()

    print("Work-around for OR operation")
    where = [
        "device_id = '5870315151' or device_id = '5881917808'",
    ]
    df = LassRawData.read_df(where=where)
    print(df)
    print()

    print("IN Operation")
    where = [
        "device_id IN :devices"
    ]
    devices = ["5870315151", "5881917808"]
    df = LassRawData.read_df(where=where, devices=devices)
    print(df)
    print()

    print("limit")
    df = LassRawData.read_df(limit=4)
    print(df)
    print()


def main():
    read_examples()


if __name__ == "__main__":
    main()
