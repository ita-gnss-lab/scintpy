"""`_orbit_propagation.py` module docstring."""  # TODOC:

from datetime import datetime, timedelta
from typing import Iterator, Literal, Tuple

import numpy as np
from loguru import logger
from skyfield.api import EarthSatellite, load
from skyfield.positionlib import ICRF, Barycentric, Geocentric
from skyfield.toposlib import GeographicPosition

from ._tle_download import get_norad_ids, get_tles
from .scenario import Scenario


def _get_sats(compact_tle_lines: list[str]) -> list[EarthSatellite]:
    ts = load.timescale()
    sats: list[EarthSatellite] = []
    for i in range(len(compact_tle_lines) // 3):
        sats.append(
            # NOTE: only one TLE is being used for each `EarthSatellite` object: "Just as today’s TLE for a satellite can only help you predict its position for a few weeks into the future, it will also be accurate for only a few weeks into the past"
            # SEE: https://rhodesmill.org/skyfield/earth-satellites.html#historical-satellite-element-sets
            EarthSatellite(
                compact_tle_lines[i * 3 + 1],  # line 1
                compact_tle_lines[i * 3 + 2],  # line 2
                compact_tle_lines[i * 3],  # line 0 (header)
                ts,
            )
        )
    return sats


def _yield_LOS_sats(
    sats: list[EarthSatellite],
    reference_time: datetime,
    receiver_pos: GeographicPosition,
    min_elevation_angle: float,
) -> Iterator[Tuple[EarthSatellite, datetime, datetime]]:
    """Yield only those satellites with line of sight.

    Parameters
    ----------
    sats : list[EarthSatellite]
        All satellites.
    reference_time : list[int]
        UTC reference time from where `scintpy` searches for satellites whose
        observation window contains `reference_time`.
    receiver_pos : GeographicPosition
        The receiver position (at the moment, a fiexed position). For receiver
        locations, `scintpy` expects an object of the `GeographicPosition` class from
        the `skyfield` package.
    minimun_elevation_angle : float
        Minimum elevation angle.

    Returns
    -------
    Iterator[Tuple[EarthSatellite, datetime, datetime]]:
        Yeild the satellite with the rise and set time, where
        rise time < `reference_time` < set time.
    """
    # create starting and ending search interval
    ts = load.timescale()
    time_plus_12h = ts.utc(reference_time + timedelta(hours=12))
    time_minus_12h = ts.utc(reference_time - timedelta(hours=12))

    events = {
        0: f"rise above {min_elevation_angle}°",
        1: "culminate",
        2: f"set below {min_elevation_angle}°",
    }
    for sat in sats:
        times, event_codes = sat.find_events(
            receiver_pos,
            time_minus_12h,
            time_plus_12h,
            altitude_degrees=min_elevation_angle,
        )
        # for all indicies of `event_codes` that indicates that the sat rises above the
        # min elevation angle
        for i in np.where(event_codes == 0)[0]:
            # prevent out-of-bound errors
            if i + 2 >= len(event_codes):
                logger.trace(
                    "The desired UTC time "
                    f"{reference_time.strftime('%Y %b %d %H:%M:%S')} is out of the "
                    f"observation window where the satellite {sat.name} is in "
                    "line-of-sight with the receiver."
                )
                break
            else:
                # times[i]   = when the sat rises above the min elevation angle
                # times[i+1] = when the sat culminates
                # times[i+2] = when the sat sets below the min elevation angle
                if (
                    times[i].utc_datetime()
                    < reference_time
                    < times[i + 2].utc_datetime()
                ):
                    rise_time = times[i].utc_datetime()
                    set_time = times[i + 2].utc_datetime()

                    logger.trace(
                        f"The satellite {sat.name} is in line-of-sight with the "
                        "receiver for the UTC time "
                        f"{reference_time.strftime('%Y %b %d %H:%M:%S')}"
                    )
                    for j in range(3):
                        logger.trace(
                            f"{events[event_codes[i+j]]} at "
                            f"{times[i+j].utc_strftime('%Y %b %d %H:%M:%S')}."
                        )
                    yield sat, rise_time, set_time
                    break


def get_sat_orbits(
    sat: EarthSatellite,
    receiver_pos: GeographicPosition,
    rise_time: datetime,
    set_time: datetime,
    sample_time: float = 100,
) -> Scenario:
    """Get satellite orbits.

    Parameters
    ----------
    sats : EarthSatellite
        The satellite whose orbit should be computed.
    sample_time : float
        Sample time (in seconds). The default is 1 second.
    rise_time: datetime
        The UTC rise time of the satellite with respect to the receiver position.
    set_time: datetime
        The UTC set time of the satellite with respect to the receiver position.
    receiver_pos : GeographicPosition
        The receiver position (at the moment, a fiexed position). For receiver
        locations, `scintpy` expects an object of the `GeographicPosition` class from
        the `skyfield` package.

    Returns
    -------
    Scenario
        A `Scenario` object which contains the receiver positioning, satellite object,
        rise and set time, and distance relative to the receiver during the whole
        obersavion window `[rise_time set_time]`, sampled at `sample_time` seconds.
    """
    total_LOS_time = (set_time - rise_time).total_seconds()
    # number of samples
    n_samples = int(total_LOS_time / sample_time)
    # init timescale
    ts = load.timescale()
    # temporal support
    rise_time = ts.from_datetime(rise_time)
    set_time = ts.from_datetime(set_time)
    time_utc = ts.linspace(rise_time, set_time, n_samples)
    # get relative position
    relative_sat_receiver_pos: ICRF | Barycentric | Geocentric = (
        sat - receiver_pos
    ).at(time_utc)
    # get altitude (elevation angle), azimuth, and relative distance
    alt, az, rel_dist = relative_sat_receiver_pos.altaz()
    # get relative velocity
    velocity = relative_sat_receiver_pos.frame_latlon_and_rates(receiver_pos)[5]
    return Scenario(
        sat,
        receiver_pos,
        time_utc,
        rel_dist_km=rel_dist.km,
        velocity_m_s=velocity.m_per_s,
        alt_deg=alt.degrees,
        az_rad=az.radians,
    )


def find_LOS_sats(
    reference_time: datetime,
    receiver_pos: GeographicPosition,
    is_online: bool = True,
    is_cache_response: bool = True,
    satellite_system: Literal["gnss", "cubesat", "gps"] = "gnss",
    username: str = "rdlfresearch@gmail.com",
    password: str = "dustrodrigo15304931",
    min_elevation_angle: float = 5,
) -> Iterator[Tuple[EarthSatellite, datetime, datetime]]:
    """Get satellite with line-of-sight with the receiver position.

    Parameters
    ----------
    reference_time : datetime
        UTC reference time from where `scintpy` searches for satellites whose
        observation window contains `reference_time`.
    receiver_pos : GeographicPosition
        The receiver position (at the moment, a fiexed position). For receiver
        locations, `scintpy` expects an object of the `GeographicPosition` class from
        the `skyfield` package.
    is_online : bool, optional
        `True`: Try to make requests to obtain satellite TLEs; `False`: Use the cached
        message instead. The requests are made to `celestrak.org` and `space-track.org`.
        By default `True`.
    is_cache_response : bool, optional
        `True`: Save overwriting previous cached data (It implies that `is_online` is
        `True`); `False`: Don't cached it. By default `True`.
    satellite_system : Literal["gnss", "cubesat", "gps"], optional
        The satellite type that `scintpy` should search for. By default "gnss".
    username : str, optional
        The username used to request data on `space-track.org`. It is used if and only
        if `is_online` is `True`. The default email "rdlfresearch@gmail.com" is used if
        the enduser does not want to enter email/password information.
    password : str, optional
        The password used to request data on `space-track.org`. It is used if and only
        if `is_online` is `True`. The default password "dustrodrigo15304931" is used if
        the enduser does not want to enter email/password information.

    Returns
    -------
    Iterator[Tuple[EarthSatellite, datetime, datetime]]
        Yeild each LOS satellite.
    """
    if receiver_pos.model.name != "WGS84":
        logger.warning(
            "A reference frame for the receiver position different than WGS84 is "
            "discouraged."
        )

    norad_ids = get_norad_ids(is_online, is_cache_response, satellite_system)
    tles = get_tles(
        norad_ids,
        reference_time,
        username,
        password,
        is_online,
        is_cache_response,
        satellite_system,
    )
    sats = _get_sats(tles)
    yield from _yield_LOS_sats(sats, reference_time, receiver_pos, min_elevation_angle)
