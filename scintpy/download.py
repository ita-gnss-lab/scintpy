"""`main_tests` docstring."""

import geom

dateTime = [2023, 9, 10, 12, 0, 1]
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

celestrak_IDs = geom._tle_download.gnss_NORAD_ID_acquire(0, 0)
unprocessed_tle_list = geom._tle_download.tle_request(
    celestrak_IDs, dateTime, username, password, 0, 0
)
grouped_tle_tuples_list = geom._tle_download.group_raw_tle_lines(unprocessed_tle_list)
grouped_tle_duplicates = geom._tle_download.find_duplicates(grouped_tle_tuples_list)
bp = 1
