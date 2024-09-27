"""test.py."""

import scintpy

# TODO: understand why `mypy` prompts an error when `(2023, 9, 10, 12, 0, 3)` is passed to `tle_request()`
date_time = (2023, 9, 10)  # , 12, 0, 3
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

celestrak_ids = scintpy.geom.gnss_NORAD_ID_acquire(False)
unprocessed_tle_list = scintpy.geom.tle_request(
    celestrak_ids, date_time, username, password, True, True
)
grouped_tle_tuples_list = scintpy.geom.group_raw_tle_lines(unprocessed_tle_list)
grouped_tle_duplicates = scintpy.geom.find_duplicates(grouped_tle_tuples_list)
bp = 1
