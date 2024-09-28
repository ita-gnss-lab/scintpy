"""test.py."""

import scintpy

date_time = [2023, 9, 10, 12, 0, 3]
receiver_pos_input = [-23.2237, -45.9009, 646]

sim_time = 600
sample_time = 0.01

username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

celestrak_ids = scintpy.geom.get_gnss_norad_id(False, False)
unprocessed_tle_list = scintpy.geom.get_tle_request(
    celestrak_ids, date_time, username, password, False, False
)

compact_tle_lines = scintpy.geom.remove_duplicates(unprocessed_tle_list, date_time)

satellite_list = scintpy.geom.get_skyfield_sats(compact_tle_lines)

reduced_sat_list = scintpy.geom.get_sat_over_horizon(
    satellite_list, sim_time, date_time, receiver_pos_input
)

bp = 1
