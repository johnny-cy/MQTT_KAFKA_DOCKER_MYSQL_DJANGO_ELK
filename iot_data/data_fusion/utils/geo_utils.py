# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np



class taichung:
    name = 'taichung'
    min_long = 120.461484
    max_long = 121.450912
    min_lat = 23.999873
    max_lat = 24.441240


class MapBuilder:
    longitude_per_km = 1 / 101.77545
    latitude_per_km = 1 / 110.9362

    @staticmethod
    def build_map_sections(min_long,
                           max_long,
                           min_lat,
                           max_lat,
                           grid_size_by_km=1):

        grid_size_of_long = MapBuilder.longitude_per_km * grid_size_by_km
        grid_size_of_lat = MapBuilder.latitude_per_km * grid_size_by_km

        longitudes = np.arange(min_long, max_long, grid_size_of_long)
        latitudes = np.arange(min_lat, max_lat, grid_size_of_lat)

        overall_coords = [([longitudes[i], latitudes[j],
                            longitudes[i] + grid_size_of_long, latitudes[j] + grid_size_of_lat])
                          for j in range(latitudes.shape[0])
                          for i in range(longitudes.shape[0])]

        return np.array(overall_coords)



def mean_pm25_in_section(station_data,
                          min_long,
                          max_long,
                          min_lat,
                          max_lat):
    mean_pm25 = None

    indices_of_stations = (station_data.lon >= min_long) & \
                            (station_data.lon <= max_long) & \
                            (station_data.lat >= min_lat) & \
                            (station_data.lat <= max_lat) & \
                            (~pd.isnull(station_data.pm2_5))

    if indices_of_stations.sum() > 0:
        mean_pm25 = station_data[indices_of_stations].pm2_5.mean()

    return mean_pm25



def distance_from_every_device_to_a_location(sensor_data,lon,lat):
    long_lat_degree_per_km = 100
    distances_of_every_device_to_this_section = np.sqrt(
                                                        (sensor_data.lon.values - lon)**2 + \
                                                        (sensor_data.lat.values - lat) ** 2
                                                        )\
                                                        *long_lat_degree_per_km
    return distances_of_every_device_to_this_section


def get_device_nearby_n_km(sensor_data,
                           lon,
                           lat,
                           km):

    distances = distance_from_every_device_to_a_location(sensor_data, lon, lat)

    devices_nearby_n_km =  sensor_data.iloc[(distances <= km)]

    if devices_nearby_n_km.shape[0] == 0:
        devices_nearby_n_km = None

    return devices_nearby_n_km

def get_device_data_in_section(df, min_lon, max_lon, min_lat, max_lat):
    output = None
    indices_of_valid_lass_data = (df.lon >= min_lon) & \
                                  (df.lon <= max_lon) & \
                                  (df.lat >= min_lat) & \
                                  (df.lat <= max_lat) & \
                                  (~pd.isnull(df.pm2_5))
    if indices_of_valid_lass_data.sum() > 0:
        output = df[indices_of_valid_lass_data]

    return output



def get_county_geo_info(county=None):
    output = None

    if county == 'taichung':
        output = taichung
    else:
        pass

    return output