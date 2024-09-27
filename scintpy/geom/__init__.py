"""`geom` package docstring."""

from ._tle_download import (
    find_duplicates,
    gnss_NORAD_ID_acquire,
    group_raw_tle_lines,
    tle_request,
)

__all__ = [
    "gnss_NORAD_ID_acquire",
    "tle_request",
    "group_raw_tle_lines",
    "find_duplicates",
]
