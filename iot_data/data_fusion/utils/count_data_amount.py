from argparse import ArgumentParser
from datetime import datetime, date, timedelta

from utils import db_access_utils, geo_utils


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_sensor_data_by_county_and__specific_hour(_datetime, county):
    station_data, iot_data, lass_data = db_access_utils.sersor_data_with_valid_pm25_in_section_by_specific_hour(_datetime,
                                                                                                                    county.min_long,
                                                                                                                   county.max_long,
                                                                                                                   county.min_lat,
                                                                                                                   county.max_lat)



    return station_data.shape[0], iot_data.shape[0], lass_data.shape[0]





if __name__ == '__main__':

    # arg_parser = ArgumentParser()
    # arg_parser.add_argument('-c', '--county', required=True)
    # arg_parser.add_argument('-d', '--datetime', required=True)
    # arg_parser.add_argument('-d2', '--datetime_2', required=False)
    # arg_parser.add_argument('-o', '--output_filename', required=False)
    # args = vars(arg_parser.parse_args())
    #
    # county = args['county']



    # _datetime = args['datetime']
    _datetime = "2018-08-16 00:00:00"
    _datetime = datetime.strptime(_datetime, "%Y-%m-%d %H:%M:%S")
    _datetime = _datetime.replace(minute=0, second=0)

    # _datetime_2 = args['datetime_2']
    _datetime_2 = "2018-08-17 00:00:00"
    if _datetime_2 is not None:
        _datetime_2 = datetime.strptime(_datetime_2, "%Y-%m-%d %H:%M:%S")
        _datetime_2 = _datetime_2.replace(minute=0, second=0)

    output_filename = args['output_filename']

    county = "taichung"

    assert county is not None, "Please select a valid county."
    assert _datetime is not None, "Specify datetime to run date fusion."

    counts_output = []

    if _datetime_2 is None:
        epa_data_amount, iot_data_amount, lass_data_amount = get_sensor_data_by_county_and__specific_hour(_datetime,
                                                                                                          geo_utils.get_county_geo_info(county))
        counts_output.append([_datetime.strftime("%Y-%m-%d %H:%M:%S"), epa_data_amount, iot_data_amount, lass_data_amount])
    else:
        start_date = date(_datetime.year, _datetime.month, _datetime.day)
        end_date = date(_datetime_2.year, _datetime_2.month, _datetime_2.day)
        for single_date in daterange(start_date, end_date):
            # print(single_date)
            for hour in range(24):
                current_datetime = datetime(single_date.year, single_date.month, single_date.day, hour)

                epa_data_amount, iot_data_amount, lass_data_amount = get_sensor_data_by_county_and__specific_hour(
                                                                                                                    current_datetime,
                                                                                                                    geo_utils.get_county_geo_info(county))
                counts_output.append([current_datetime.strftime("%Y-%m-%d %H:%M:%S"), epa_data_amount, iot_data_amount, lass_data_amount])

    print(counts_output)