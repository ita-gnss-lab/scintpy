"""Scenario of sat-receiver trajectory during a time interval."""

from dataclasses import dataclass

import numpy as np
from skyfield.api import EarthSatellite
from skyfield.timelib import Time
from skyfield.toposlib import GeographicPosition


@dataclass
class Scenario:
    """Scenario of sat-receiver trajectory during a time interval."""

    satelite: EarthSatellite
    receiver: GeographicPosition  # NOTE: fixed receiver
    time: Time
    rel_dist_km: np.ndarray
    velocity_m_s: np.ndarray
    alt_deg: np.ndarray
    az_rad: np.ndarray
