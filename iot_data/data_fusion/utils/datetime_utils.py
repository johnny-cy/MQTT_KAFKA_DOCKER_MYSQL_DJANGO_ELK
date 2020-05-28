# -*- coding: UTF-8 -*-
import datetime

def get_str_datetimes_by_current_hour_and_next():
    current_datetime = datetime.datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour

    if hour == 23:
        current_date = datetime.date(year, month, day)
        date_by_next_hour = current_date + datetime.timedelta(days=1)
        year_by_next_hour = date_by_next_hour.year
        month_by_next_hour = date_by_next_hour.month
        day_by_next_hour = date_by_next_hour.day
        next_hour = 0
        # print(current_date, date_by_next_hour)
    else:
        year_by_next_hour = year
        month_by_next_hour = month
        day_by_next_hour = day
        next_hour = hour + 1




    data_time_range_start = "'{year}-{month}-{day} {hour}:00:00'"\
                            .format(year=year, month=month, day=day, hour=hour)

    data_time_range_end = "'{year}-{month}-{day} {next_hour}:00:00'"\
                            .format(year=year_by_next_hour, month=month_by_next_hour, day=day_by_next_hour, next_hour=next_hour)

    return data_time_range_start, data_time_range_end


def get_str_datetime_by_current_hour():
    current_datetime = datetime.datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour

    current_hor = "'{year}-{month}-{day} {hour}:00:00'"\
                            .format(year=year, month=month, day=day, hour=hour)

    return current_hor

def get_str_datetime_by_next_hour():
    current_datetime = datetime.datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour + 1

    current_hor = "'{year}-{month}-{day} {hour}:00:00'"\
                            .format(year=year, month=month, day=day, hour=hour)

    return current_hor

def get_str_datetime_by_current_hour_by_datetime_obj(_datetime_obj):
    year = _datetime_obj.year
    month = str(_datetime_obj.month).zfill(2)
    day = str(_datetime_obj.day).zfill(2)
    hour = str(_datetime_obj.hour).zfill(2)

    current_hor = "'{year}-{month}-{day} {hour}:00:00'"\
                            .format(year=year, month=month, day=day, hour=hour)
    return current_hor

def get_str_datetime_by_next_hour_by_datetime_obj(_datetime_obj):
    year = _datetime_obj.year
    month = _datetime_obj.month
    day = _datetime_obj.day
    hour = _datetime_obj.hour

    if hour == 23:
        current_date = datetime.date(year, month, day)
        date_by_next_hour = current_date + datetime.timedelta(days=1)
        year_by_next_hour = date_by_next_hour.year
        month_by_next_hour = date_by_next_hour.month
        day_by_next_hour = date_by_next_hour.day
        next_hour = 0


    else:
        year_by_next_hour = year
        month_by_next_hour = month
        day_by_next_hour = day
        next_hour = hour + 1

    year_by_next_hour = str(year_by_next_hour).zfill(2)
    month_by_next_hour = str(month_by_next_hour).zfill(2)
    day_by_next_hour = str(day_by_next_hour).zfill(2)
    next_hour = str(next_hour).zfill(2)


    current_hor = "'{year}-{month}-{day} {hour}:00:00'"\
                            .format(year=year_by_next_hour,
                                    month=month_by_next_hour,
                                    day=day_by_next_hour,
                                    hour=next_hour)
    return current_hor


def get_datetime_object_by_current_hour():
    current_datetime = datetime.datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour

    output_object = datetime.datetime(year, month, day, hour)

    return output_object
