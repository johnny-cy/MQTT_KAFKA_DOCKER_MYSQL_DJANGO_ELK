# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd

def standardlized_pm25(df):
    df.pm2_5 = df.pm2_5.apply(
        lambda val: val
        if not any(char in ['*', '#', 'x'] for char in str(val)) and val is not None
        else np.nan
    )

    return df

def resample_pm25_mean_by_hour(df):
    df.index = pd.DatetimeIndex(df.time)
    df = df.groupby([pd.Grouper(freq='1H'), 'device_id']) \
        .mean() \
        .reset_index()

    return df



def interpolate(values_without_fuhshion):
    # print(values_without_fuhshion.shape)
    flatten = values_without_fuhshion.ravel()

    clone = flatten.copy()

    for i in range(flatten.shape[0]):
        index_row = i // 101
        index_col = i % 101
        # print(flatten[i])
        if np.isnan(flatten[i]):
            # print('Null!')

            try:
                interpolated_value = 0
                number_of_nearby_areas_the_have_values = 0

                if index_col > 0:
                    grid_on_left = flatten[i - 1]
                    if np.isnan(grid_on_left):
                        grid_on_left = np.nan
                else:
                    grid_on_left = np.nan

                if index_col < 100:
                    grid_on_right = flatten[i + 1]
                    if np.isnan(grid_on_right):
                        grid_on_right = np.nan
                else:
                    grid_on_right = np.nan

                if index_row > 0:
                    grid_on_top = flatten[i - 101]
                    if np.isnan(grid_on_top):
                        grid_on_top = np.nan
                else:
                    grid_on_top = np.nan

                if index_row < 48:
                    grid_on_bottom = flatten[i + 101]
                    if np.isnan(grid_on_bottom):
                        grid_on_bottom = np.nan
                else:
                    grid_on_bottom = np.nan
                ##################################################
                # 左上角
                if index_col > 0 and index_row > 0:
                    grid_on_top_left = flatten[i - 101 - 1]
                    if np.isnan(grid_on_top_left):
                        grid_on_top_left = np.nan
                else:
                    grid_on_top_left = np.nan
                # 右上角
                if index_col < 100 and index_row > 0:
                    grid_on_top_right = flatten[i + 1 - 101]
                    if np.isnan(grid_on_top_right):
                        grid_on_top_right = np.nan
                else:
                    grid_on_top_right = np.nan
                # 左下角
                if index_col > 0 and index_row < 48:
                    grid_on_bottom_left = flatten[i + 101 - 1]
                    if np.isnan(grid_on_bottom_left):
                        grid_on_bottom_left = np.nan
                else:
                    grid_on_bottom_left = np.nan
                # 右下角
                if index_col < 100 and index_row < 48:
                    grid_on_bottom_right = flatten[i + 101 + 1]
                    if np.isnan(grid_on_bottom_right):
                        grid_on_bottom_right = np.nan
                else:
                    grid_on_bottom_right = np.nan



                if not np.isnan(grid_on_left):
                    interpolated_value += grid_on_left
                    number_of_nearby_areas_the_have_values += 1
                if not np.isnan(grid_on_right):
                    interpolated_value += grid_on_right
                    number_of_nearby_areas_the_have_values += 1
                if not np.isnan(grid_on_top):
                    interpolated_value += grid_on_top
                    number_of_nearby_areas_the_have_values += 1
                if not np.isnan(grid_on_bottom):
                    interpolated_value += grid_on_bottom
                    number_of_nearby_areas_the_have_values += 1

                if not np.isnan(grid_on_top_left):
                    interpolated_value += grid_on_top_left
                    number_of_nearby_areas_the_have_values += 1
                if not np.isnan(grid_on_top_right):
                    interpolated_value += grid_on_top_right
                    number_of_nearby_areas_the_have_values += 1
                if not np.isnan(grid_on_bottom_left):
                    interpolated_value += grid_on_bottom_left
                    number_of_nearby_areas_the_have_values += 1
                if not np.isnan(grid_on_bottom_right):
                    interpolated_value += grid_on_bottom_right
                    number_of_nearby_areas_the_have_values += 1

                if number_of_nearby_areas_the_have_values != 0:
                    interpolated_value = interpolated_value / number_of_nearby_areas_the_have_values
                    # print(interpolated_value)

                if interpolated_value != 0:
                    # print(grid_on_left, np.isnan(grid_on_left))
                    # print(grid_on_right, np.isnan(grid_on_right))
                    # print(grid_on_top, np.isnan(grid_on_top))
                    # print(grid_on_bottom, np.isnan(grid_on_bottom))
                    # print(grid_on_top_left, np.isnan(grid_on_top_left))
                    # print(grid_on_top_right, np.isnan(grid_on_top_right))
                    # print(grid_on_bottom_left, np.isnan(grid_on_bottom_left))
                    # print(grid_on_bottom_right, np.isnan(grid_on_bottom_right))


                    clone[i] = interpolated_value
            except Exception as e:
                pass
                # print(i)

        else:
            pass
            # print(type(flatten[i]))

    return clone