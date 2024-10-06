"""test.py."""

import scintpy

date_time = [2024, 10, 4, 12, 0, 30]
receiver_pos_input = [19.8206, 155.4681, 4.2]

sim_time = 400
sample_time = 10

username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"
satellite_system = "cubesat"
minimum_elev_angle = 10
celestrak_ids = scintpy.geom.get_gnss_norad_id(False, False, satellite_system)
unprocessed_tle_list = scintpy.geom.get_tle_request(
    celestrak_ids, date_time, username, password, False, False, satellite_system
)

compact_tle_lines = scintpy.geom.remove_duplicates(unprocessed_tle_list, date_time)

satellite_list = scintpy.geom.get_skyfield_sats(compact_tle_lines)

reduced_sat_list = scintpy.geom.get_sat_over_horizon(
    satellite_list, sim_time, date_time, receiver_pos_input, minimum_elev_angle
)

sat_pos_timeseries = scintpy.geom.get_sat_orbit_timeseries(
    reduced_sat_list, sim_time, sample_time, date_time, receiver_pos_input
)

scintpy.geom.skyplot_sat_orbit_timeseries(sat_pos_timeseries)
bp = 1
