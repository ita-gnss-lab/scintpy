"""`_orbit_propagation.py` module docstring."""

from skyfield.api import EarthSatellite, load


def skyfield_compute_orbits(compact_tle_lines: list[str]) -> list[EarthSatellite]:
    ts = load.timescale()
    satellites_list: list[EarthSatellite] = []
    for i in range(len(compact_tle_lines) // 3):
        satellites_list.append(
            EarthSatellite(
                compact_tle_lines[i * 3 + 1],
                compact_tle_lines[i + 2],
                compact_tle_lines[i],
                ts,
            )
        )
    return satellites_list
