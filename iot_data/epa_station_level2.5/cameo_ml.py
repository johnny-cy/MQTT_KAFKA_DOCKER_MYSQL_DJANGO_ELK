#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import pickle
import math
import logging

import numpy as np
import pandas as pd
import dateutil
from scipy.special import erf

from epa.models import EpaStationTextarRawData, EpaStationTextarAbnormal
from epa.logging import get_logger


logger = get_logger(__name__)


def extract_mark(df):
    df = df.fillna("NoValue")
    s = df.stack(df.columns.names)
    regex = "(-?\d+\.?\d*|NR)?([\*#x]|NoValue)?"
    df_value_mark = s.astype(str).str.extract(regex, expand=False)

    df_value = df_value_mark.iloc[:, 0].unstack(["station", "item"])
    df_mark = df_value_mark.iloc[:, 1].unstack(["station", "item"])

    return df_value, df_mark


def extract_features(df, main_feature="PM10"):
    df_value, df_mark = extract_mark(df)
    df = df_value.replace("NR", 0)\
                 .apply(pd.to_numeric)

    def _shift(df, periods, main_feature):
        df = df.sort_index(axis=1).loc[:, (slice(None), main_feature)].shift(periods)
        column1 = df.columns.get_level_values(0)
        column2 = ["{}-{}".format(v, periods) for v in df.columns.get_level_values(1)]
        df.columns = pd.MultiIndex.from_tuples(list(zip(column1, column2)))
        return df

    df = pd.concat([df] + [_shift(df, h, main_feature) for h in range(1, 7)], axis=1)

    def _wind_dir(df, direct, degree_range):
        df_wind_dir = df.sort_index(axis=1).loc[:, (slice(None), "WIND_DIRECT")]
        if degree_range[0] > degree_range[1]:
            _df = (df_wind_dir > degree_range[0]) | (df_wind_dir < degree_range[1])
        else:
            _df = (df_wind_dir > degree_range[0]) & (df_wind_dir < degree_range[1])
        tuples = [(a, "{}({})".format(b, direct)) for a, b in df_wind_dir.columns.get_values()]
        _df.columns = pd.MultiIndex.from_tuples(tuples, names=("station", "item"))
        return _df

    wind = {
            "N": [337.5, 22.5],
            "NE": [22.5, 67.5],
            "E": [67.5, 112.5],
            "SE": [112.5, 157.5],
            "S": [157.5, 202.5],
            "SW": [202.5, 247.5],
            "W": [247.5, 292.5],
            "NW": [292.5, 337.5],
            }

    df_wind = pd.concat([_wind_dir(df, d, r) for d, r in wind.items()], axis=1)

    df = pd.concat([df, df_wind], axis=1)

    df = df.stack("station")

    columns_for_ratio = ['CH4', 'CO', 'NO', 'NO2', 'NOx', 'O3', 'PM2.5',
            'PM10', 'RAINFALL', 'SO2', 'WIND_SPEED', "Top1", "Top2", "Top3"]
    for column in [col for col in columns_for_ratio if col != main_feature]:
        if column in df.columns:
            new_column = "{}/{}".format(column, main_feature)
            df[new_column] = df[column] / df[main_feature]

    columns_to_drop = ['AMB_TEMP', 'NMHC', 'PH_RAIN','RAIN_COND', 'RH',
            'CO2', 'THC', 'UVB', 'WD_HR', 'WS_HR', "Top1", "Top2", "Top3"]
    for col in columns_to_drop:
        if col in df.columns:
            df = df.drop(col, axis=1)


    #YK: replace "inf"
    df = df.replace(float("Inf"), np.NaN)
    df = df.replace(float("-Inf"), np.NaN)


    #YK: combine Y
    s_mark = df_mark.stack("station")[main_feature].rename("Mark")
    s_mark_shift = df_mark.shift().stack("station")[main_feature].rename("Mark")
    y = s_mark.notnull().rename("Y")
    y_shift = s_mark_shift.notnull().rename("Y Prev")
    df = pd.concat([df, y, y_shift], axis=1)

    df = df.fillna(0).astype(float)

    return df, s_mark


def split_x_y(df):
    y = df["Y"]
    x = df[[col for col in df.columns.values.tolist() if col != "Y"]]
    return x, y


def random_forest(df, pickle_file, main_feature="PM10"):
    with open(pickle_file, "rb") as f:
        clf = pickle.load(f)

    df_test, df_mark = extract_features(df, main_feature)
    x_test, y_test = split_x_y(df_test)

    result = clf.predict(x_test)
    s_result = pd.Series(result, index=y_test.index)
    return s_result.astype(np.int8)


def calculate_std_err(df):
    df_mean = df.mean(axis=1, level="item")
    df_std = df.std(axis=1, level="item")
    df_stderr = df.sub(df_mean, level="item").div(df_std, level="item")
    return df_stderr


def mark_threshold(df, threshold):
    df_high = (df > threshold)
    return df_high


def calculate_score(df):
    return erf(np.absolute(df) / math.sqrt(2))


def calculate_rolling_std_err(df, window_size=6):
    window_format = "{}H".format(window_size)
    df_rolling_mean = df.rolling(window_format, min_periods=window_size).mean()
    df_rolling_std = df.rolling(window_format, min_periods=window_size).std()
    df_rolling_stderr = (df - df_rolling_mean) / df_rolling_std
    return df_rolling_stderr


def std(df, main_feature="PM10", threshold=1.9488):
    #'PM10': 1.948836587,    # 北
    #"PM10": 1.941064979,    # 中
    #"PM10": 1.947948796,    # 南
    #YK: TODO
    threshold = 1.948836587

    df_value, df_mark = extract_mark(df)
    df_value = df_value.replace("NR", 0).apply(pd.to_numeric)

    df_stderr = calculate_std_err(df_value)
    df_stderr_score = calculate_score(df_stderr)

    df_rolling_stderr = calculate_rolling_std_err(df_value, window_size=6)
    df_rolling_score = calculate_score(df_rolling_stderr)

    df_score = df_stderr_score + df_rolling_score
    df_high = mark_threshold(df_score, threshold)

    df_high = df_high.sort_index(axis=1)\
                     .loc[:, (slice(None), main_feature)]
    df_high.columns = df_high.columns.droplevel(1)
    return df_high.stack().astype(np.int8)


def combine_nearest_top3(df, main_feature):
    def _combine_nearest(df1, df2):
        result_dfs = []
        for station in df1.columns.levels[0]:
            if station not in df2.index:
                continue
            _df = df1.loc[:, station]
            nearest_value = [_df]
            for i, n in enumerate(df2.loc[station]):
                try:
                    x = df1.loc[:, (n, main_feature)].rename("Top{}".format(i+1)).to_frame()
                    nearest_value.append(x)
                except KeyError:
                    pass
            _df = pd.concat(nearest_value, axis=1)
            _df.columns = pd.MultiIndex.from_product(\
                            [[station], _df.columns],
                            names=["station", "item"],
                            )
            result_dfs.append(_df)
        return pd.concat(result_dfs, axis=1)

    df_nearest = pd.read_csv("./data/76_station_nearest_4.csv",
                        index_col=0,
                        ).drop("0", axis=1)
    return _combine_nearest(df, df_nearest)


def predict(main_feature, start, end, pickle_file):
    df = EpaStationTextarRawData.db.read(
        where=[
            "time >= :start",
            "time <= :end",
        ],
        start=start, end=end
    ).as_df()

    df["station"] = df["name"]\
                    .str.split("-", expand=True)[3]\
                    .str.split("[", expand=True)[0]\
                    .str.slice(0, -2)
    df = df[df["station"].notna()]

    df = df.set_index(["time", "station"])
    df.columns = df.columns.str.upper()
    df.columns.name = "item"
    df = df.rename(columns={
        "PM2_5": "PM2.5",
        "NOX": "NOx",
    })
    columns = ['CH4', 'CO', 'NO', 'NO2', 'NOx', 'O3', 'PM2.5',
               'PM10', 'RAINFALL', 'SO2', 'WIND_DIRECT', 'WIND_SPEED']
    df = df[columns]
    df = df.stack(dropna=False) \
           .unstack(["station", "item"]) \
           .sort_index(axis=1)

    df = combine_nearest_top3(df, main_feature)

    result_1 = random_forest(df, pickle_file, main_feature)
    result_2 = std(df, main_feature)
    result = result_1.add(result_2, fill_value=0.0)

    result = result.replace(0, "L") \
                   .replace(1, "M") \
                   .replace(2, "H")

    # for value lookup
    df = df.stack(["station", "item"])

    for i, x in result.rename("level").reset_index().iterrows():
        x = x.to_dict()
        x["item"] = main_feature
        obj = EpaStationTextarAbnormal(**x)
        obj.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start",
            help="start time")
    parser.add_argument("-e", "--end",
            help="end time")
    parser.add_argument("-f", "--feature", default="PM10",
            help='main feature, use "all" for all 8 features')

    args = parser.parse_args()
    main_feature = args.feature
    end = dateutil.parser.parse(args.end)  if args.end else \
            datetime.datetime.now()
    start = dateutil.parser.parse(args.start) if args.start else \
            end - datetime.timedelta(days=1)

    if main_feature == "all":
        features = ['CO', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM2.5', 'SO2']
    else:
        features = [main_feature]

    for feature in features:
        pickle_file = "./data/random_forest_{}.pkl".format(feature)
        predict(feature, start, end, pickle_file)


if __name__ == "__main__":
    main()

