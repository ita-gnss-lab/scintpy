"""`geom` package docstring."""  # TODOC:

from ._geom_plots import plot_sat_orbits
from ._orbit_propagation import (
    get_sat_orbits,
    get_sat_over_horizon,
    get_skyfield_sats,
    save_sat_pos,
)
from ._tle_download import (
    get_norad_ids,
    get_tle_request,
    remove_duplicates,
)

__all__ = [
    "get_norad_ids",
    "get_tle_request",
    "remove_duplicates",
    "get_skyfield_sats",
    "get_sat_orbits",
    "get_sat_over_horizon",
    "plot_sat_orbits",
    "save_sat_pos",
]
