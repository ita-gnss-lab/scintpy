"""test.py."""

import scintpy

date_time = [2023, 9, 10, 12, 0, 3]
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

celestrak_ids = scintpy.geom.get_gnss_norad_id(False, False)
unprocessed_tle_list = scintpy.geom.get_tle_request(
    celestrak_ids, date_time, username, password, False, False
)
# compact_tle_list = scintpy.geom.remove_duplicates(unprocessed_tle_list, date_time)

# full_satellites_list = scintpy.geom.skyfield_compute_orbits(compact_tle_list)
# bp = 1
