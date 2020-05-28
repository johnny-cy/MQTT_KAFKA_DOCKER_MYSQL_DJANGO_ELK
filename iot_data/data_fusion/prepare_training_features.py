import pandas as pd
import numpy as np

from utils import geo_utils, db_access_utils, datetime_utils, preprocessing_utils


def saving_training_data(county, distance_threshold):
    map_sections = geo_utils.MapBuilder.build_map_sections(county.min_long,
                                                           county.max_long,
                                                           county.min_lat,
                                                           county.max_lat)

    station_data, iot_data, lass_data = db_access_utils.sersor_data_in_section_by_overall_time(county.min_long,
                                                                                               county.max_long,
                                                                                               county.min_lat,
                                                                                               county.max_lat)

    training_data = []

    for i, (min_lon, min_lat, max_lon, max_lat) in enumerate(map_sections):

        if lass_data is not None:
            mean_lon, mean_lat = (min_lon + max_lon) / 2, (min_lat + max_lat) / 2
            lass_data_in_this_area = geo_utils.get_device_data_in_section(lass_data, min_lon, max_lon, min_lat, max_lat)
            if lass_data_in_this_area is not None:
                resampled_lass_data = preprocessing_utils.resample_pm25_mean_by_hour(lass_data_in_this_area)
                eap_data_in_this_area = geo_utils.get_device_nearby_n_km(station_data, mean_lon, mean_lat,
                                                                         distance_threshold)
                iot_data_in_this_area = geo_utils.get_device_nearby_n_km(iot_data, mean_lon, mean_lat,
                                                                         distance_threshold)

                iot_and_stations_in_this_section = None

                if eap_data_in_this_area is not None and iot_data_in_this_area is not None:
                    iot_and_stations_in_this_section = pd.concat([eap_data_in_this_area, iot_data_in_this_area])
                elif eap_data_in_this_area is not None:
                    iot_and_stations_in_this_section = eap_data_in_this_area
                elif iot_data_in_this_area is not None:
                    iot_and_stations_in_this_section = iot_data_in_this_area

                if iot_and_stations_in_this_section is not None:
                    for i, row in resampled_lass_data.iterrows():
                        matched_epa_data = iot_and_stations_in_this_section[
                            iot_and_stations_in_this_section.time == row.time]
                        if not matched_epa_data.empty:
                            # print('lass', row, sep='\n')
                            # print('epa', matched_epa_data, sep='\n')
                            for j, row_2 in matched_epa_data.iterrows():
                                training_data.append([row.pm2_5, row_2.pm2_5])
    training_data = np.array(training_data)
    # print(training_data.shape)
    output = pd.DataFrame(training_data, columns=['trainx', 'train_y'])
    output.to_csv('data/training_feature_using_nearby_{}_km_data.csv'.format(distance_threshold), index=False)


if __name__ == '__main__':
    county = geo_utils.taichung
    saving_training_data(county, 6)