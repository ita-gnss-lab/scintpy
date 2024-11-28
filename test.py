"""_summary_."""

from datetime import datetime, timezone

from skyfield.api import wgs84

import scintpy

scintpy.setup_log("TRACE")

reference_time = datetime(2024, 10, 28, 8, 54, 0, tzinfo=timezone.utc)
# São José dos Campos
receiver_pos = wgs84.latlon(-23.20713241666, -45.861737777, 605.088)

scenarios = []
for sat, rise_time, set_time in scintpy.geom.find_LOS_sats(
    reference_time, receiver_pos, is_online=False
):
    scenarios.append(
        scintpy.geom.get_sat_orbits(sat, receiver_pos, rise_time, set_time)
    )

scintpy.geom.plot_sat_orbits(scenarios, reference_time)

bp = 1
