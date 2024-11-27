"""`_orbit_propagation.py` module docstring."""  # TODOC:

from datetime import datetime, timedelta
from typing import Generator, Literal, Tuple

import numpy as np
from loguru import logger
from skyfield.api import EarthSatellite, load, utc, wgs84
from skyfield.positionlib import ICRF, Barycentric, Geocentric
from skyfield.toposlib import GeographicPosition

from ._tle_download import get_norad_ids, get_tles
from .scenario import Scenario


def _get_sats(compact_tle_lines: list[str]) -> list[EarthSatellite]:
    ts = load.timescale()
    satellites_list: list[EarthSatellite] = []
    for i in range(len(compact_tle_lines) // 3):
        satellites_list.append(
            # NOTE: only one TLE is being used for a `EarthSatellite` object: "Just as today’s TLE for a satellite can only help you predict its position for a few weeks into the future, it will also be accurate for only a few weeks into the past"
            # SEE: https://rhodesmill.org/skyfield/earth-satellites.html#historical-satellite-element-sets
            EarthSatellite(
                compact_tle_lines[i * 3 + 1],  # line 1
                compact_tle_lines[i * 3 + 2],  # line 2
                compact_tle_lines[i * 3],  # line 0 (header)
                ts,
            )
        )
    return satellites_list


def _yield_LOS_sats(
    sats: list[EarthSatellite],
    date_time: list[int],
    receiver_pos: GeographicPosition,
    min_elevation_angle: float,
) -> Generator[Tuple[EarthSatellite, datetime, datetime]]:
    """Return a list with only those with line of sight.

    Parameters
    ----------
    sats : list[EarthSatellite]
        Satellite list obtained from _get_sats function.
    date_time : list[int]
        [Year,Month,Day,Hours,Minutes,seconds] list.
    receiver_pos : list[float]
        longitude [rad], latitude [rad] and height [m]
    minimun_elevation_angle : float
        Minimum elevation angle acceptable.

    Returns
    -------
    list[bool]
    """
    # create start and the end datetime
    reference_time = datetime(*date_time, tzinfo=utc)  # type: ignore # HACK: ignore unpacking `*` and multiple values for keyword error from `mypy`
    # create starting and ending search interval
    ts = load.timescale()
    time_plus_12h = ts.utc(reference_time + timedelta(hours=12))
    time_minus_12h = ts.utc(reference_time - timedelta(hours=12))

    for sat in sats:
        times, event_codes = sat.find_events(
            receiver_pos,
            time_minus_12h,
            time_plus_12h,
            altitude_degrees=min_elevation_angle,
        )
        events = {
            0: f"rise above {min_elevation_angle}°",
            1: "culminate",
            2: f"set below {min_elevation_angle}°",
        }
        # for all indicies where the sat rise above the min elevation angle
        for i in np.where(event_codes == 0)[0]:
            # prevent out-of-bound errors
            if i + 2 >= len(event_codes):
                break
            else:
                # times[i]   = when the sat rise above the min elevation angle
                # times[i+1] = when the sat culminates
                # times[i+2] = when the sat set below the min elevation angle
                if (
                    times[i].utc_datetime()
                    < reference_time
                    < times[i + 2].utc_datetime()
                ):
                    rise_time = times[i].utc_datetime()
                    set_time = times[i + 2].utc_datetime()

                    logger.trace(f"Satellite name: {sat.name}")
                    for j in range(3):
                        logger.trace(
                            f'{times[i+j].utc_strftime("%Y %b %d %H:%M:%S")}: '
                            f'{events[event_codes[i+j]]}'
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
        _description_
    sample_time : float
        Sample time (in seconds). The default is 1 second.
    date_time : list[int]
        _description_
    receiver_pos : list[float]
        _description_

    Returns
    -------
    Tuple[np.ndarray, list[str], list[datetime]]
        _description_
    """
    receiver_pos_: GeographicPosition = wgs84.latlon(*receiver_pos)
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
    relative_sat_receiver_pos_: ICRF | Barycentric | Geocentric = (
        sat - receiver_pos_
    ).at(time_utc)
    # get altitude (elevation angle), azimuth, and relative distance
    alt, az, rel_dist = relative_sat_receiver_pos_.altaz()
    # get relative velocity
    velocity = relative_sat_receiver_pos_.frame_latlon_and_rates(receiver_pos_)[5]
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
    date_time: list[int],
    receiver_pos: GeographicPosition,
    is_online: bool = True,
    is_cache_response: bool = True,
    satellite_system: Literal["gnss", "cubesat", "gps"] = "gnss",
    username: str = "rdlfresearch@gmail.com",
    password: str = "dustrodrigo15304931",
    min_elevation_angle: float = 5,
) -> Generator[Tuple[EarthSatellite, datetime, datetime]]:
    """Get satellite over horizon.

    Parameters
    ----------
    date_time : list[int]
        _description_
    receiver_pos : _type_, optional
        _description_, by default list[float]
    is_online : bool, optional
        _   description_, by default True
    is_cache_response : bool, optional
        _description_, by default False
    satellite_system : Literal["gnss", "cubesat", "gps"], optional
        _description_, by default "gnss"
    username : str, optional
        _description_, by default "rdlfresearch@gmail.com"
    password : str, optional
        _description_, by default "dustrodrigo15304931"

    Returns
    -------
    list[EarthSatellite]
        _description_
    """
    # NOTE: WGS84 (World Geodetic System 1984) is a reference system used by the satellite navigation systems like GPS and is used in various mapping applications.
    # SEE: https://en.wikipedia.org/wiki/World_Geodetic_System
    receiver_pos: GeographicPosition = wgs84.latlon(*receiver_pos)  # type: ignore

    norad_ids = get_norad_ids(is_online, is_cache_response, satellite_system)
    tles = get_tles(
        norad_ids,
        date_time,
        username,
        password,
        is_online,
        is_cache_response,
        satellite_system,
    )
    sats = _get_sats(tles)
    yield from _yield_LOS_sats(sats, date_time, receiver_pos, min_elevation_angle)
