"""test.py."""

import scintpy

dateTime = [2023, 9, 10, 12, 0, 3]
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

celestrak_IDs = scintpy.geom.gnss_NORAD_ID_acquire(False, True)
unprocessed_tle_list = scintpy.geom.tle_request(
    celestrak_IDs, dateTime, username, password, 0, 0
)
grouped_tle_tuples_list = scintpy.geom.group_raw_tle_lines(unprocessed_tle_list)
grouped_tle_duplicates = scintpy.geom.find_duplicates(grouped_tle_tuples_list)
bp = 1
