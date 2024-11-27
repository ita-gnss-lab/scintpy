"""_summary_."""

import scintpy

date_time = [2024, 10, 28, 8, 54, 0]  # [2024, 10, 5, 9, 10, 20]
# São José dos Campos
receiver_pos = [-23.20713241666, -45.861737777, 605.088]

scenarios = []
for sat, rise_time, set_time in scintpy.geom.find_LOS_sats(
    date_time, receiver_pos, is_online=False
):
    scenarios.append(
        scintpy.geom.get_sat_orbits(sat, receiver_pos, rise_time, set_time)
    )

scintpy.geom.plot_sat_orbits(scenarios, date_time)

bp = 1
