"""test.py."""

import scintpy

date_time = [2024, 10, 5, 10, 38, 0]
receiver_pos_input = [23.2146, 45.8614, 646]

sim_time = 10000
sample_time = 100

username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"
satellite_system = "gnss"
minimum_elev_angle = 0
celestrak_ids = scintpy.geom.get_gnss_norad_id(False, False, satellite_system)
unprocessed_tle_list = scintpy.geom.get_tle_request(
    celestrak_ids, date_time, username, password, False, False, satellite_system
)

compact_tle_lines = scintpy.geom.remove_duplicates(unprocessed_tle_list, date_time)

satellite_list = scintpy.geom.get_skyfield_sats(compact_tle_lines)

reduced_sat_list = scintpy.geom.get_sat_over_horizon(
    satellite_list, sim_time, date_time, receiver_pos_input, minimum_elev_angle
)

sat_pos_timeseries, sat_ids = scintpy.geom.get_sat_orbits(
    reduced_sat_list, sim_time, sample_time, date_time, receiver_pos_input
)

scintpy.geom.plot_sat_orbits(sat_pos_timeseries, sat_ids)
bp = 1
