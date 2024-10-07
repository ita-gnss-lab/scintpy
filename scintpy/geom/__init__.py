"""`geom` package docstring."""  # TODOC:

from ._geom_plots import plot_sat_orbits
from ._orbit_propagation import (
    get_sat_orbits,
    get_sat_over_horizon,
    get_skyfield_sats,
)
from ._tle_download import (
    get_gnss_norad_id,
    get_tle_request,
    remove_duplicates,
)

__all__ = [
    "get_gnss_norad_id",
    "get_tle_request",
    "remove_duplicates",
    "get_skyfield_sats",
    "get_sat_orbits",
    "get_sat_over_horizon",
    "plot_sat_orbits",
]
