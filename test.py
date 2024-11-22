"""test.py."""

# I used these two libraries when i was testing Daniele's algorithm
# import re
# from pathlib import Path

import scintpy

date_time = [2024, 10, 28, 8, 54, 0]  # [2024, 10, 5, 9, 10, 20]
receiver_pos_input = [-23.20713241666, -45.861737777, 605.088]

sim_time = 600
sample_time = 1

username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"
satellite_system = "cubesat"
minimum_elev_angle = 0
# TODO: When i was comparing this code with the results that Daniele was getting in MATLAB, i noticed that this methodology of picking up the ids on celestrak website and going to space-track.org to download the TLE is working pretty well for any date with the exception to the current one. We need to correct that later.
# False, True
celestrak_ids = scintpy.geom.get_gnss_norad_id(False, False, satellite_system)
unprocessed_tle_list = scintpy.geom.get_tle_request(
    celestrak_ids, date_time, username, password, False, False, satellite_system
)

compact_tle_lines = scintpy.geom.remove_duplicates(unprocessed_tle_list, date_time)
# with open("gp_test.txt") as file:  # noqa: E501
#     space_track_text = file.read()

# satellite_list = scintpy.geom.get_skyfield_sats(space_track_text.splitlines())
satellite_list = scintpy.geom.get_skyfield_sats(compact_tle_lines)

reduced_sat_list = scintpy.geom.get_sat_over_horizon(
    satellite_list, sim_time, date_time, receiver_pos_input, minimum_elev_angle
)

sat_pos_timeseries, sat_ids, datetime_ts = scintpy.geom.get_sat_orbits(
    reduced_sat_list, sim_time, sample_time, date_time, receiver_pos_input
)

scintpy.geom.save_sat_pos(sat_pos_timeseries, sat_ids, satellite_system)
scintpy.geom.plot_sat_orbits(sat_pos_timeseries, sat_ids, datetime_ts)
bp = 1
