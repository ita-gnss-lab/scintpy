"""`_orbit_propagation.py` module docstring."""  # TODOC:

from datetime import datetime, timedelta
from typing import Literal, Tuple

import numpy as np
from skyfield.api import EarthSatellite, load, utc, wgs84

from ._tle_download import get_norad_ids, get_tles


def _get_sats(compact_tle_lines: list[str]) -> list[EarthSatellite]:
    ts = load.timescale()
    satellites_list: list[EarthSatellite] = []
    for i in range(len(compact_tle_lines) // 3):
        satellites_list.append(
            EarthSatellite(
                compact_tle_lines[i * 3 + 1],
                compact_tle_lines[i * 3 + 2],
                compact_tle_lines[i * 3],
                ts,
            )
        )
    return satellites_list


def _get_sat_over_horizon(
    satellite_list: list[EarthSatellite],
    sim_time: float,
    date_time: list[int],
    receiver_pos: list[float],
    minimum_elevation_angle: float,
) -> list[bool]:
    """Return a list with only those with line of sight.

    Parameters
    ----------
    satellite_list : list[EarthSatellite]
        Satellite list obtained from _get_sats function.
    sim_time : float
        Desired amount of time in seconds.
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
    start_time_datetime = datetime(*date_time, tzinfo=utc)  # type: ignore # NOTE: ignore unpacking `*` type error from `mypy`
    end_time_datetime = start_time_datetime + timedelta(seconds=sim_time)

    ts = load.timescale()
    start_time_utc = ts.from_datetime(start_time_datetime)  # type: ignore
    end_time_utc = ts.from_datetime(end_time_datetime)
    receiver_pos = wgs84.latlon(*receiver_pos)  # type: ignore
    i = 0
    while i < len(satellite_list):
        init_relative_pos = (satellite_list[i] - receiver_pos).at(start_time_utc)
        end_relative_pos = (satellite_list[i] - receiver_pos).at(end_time_utc)
        alt_init, _, _ = init_relative_pos.altaz()
        alt_end, _, _ = end_relative_pos.altaz()
        # print(init_relative_pos.position.km[2],end_relative_pos.position.km[2])
        if (
            alt_init.degrees < minimum_elevation_angle
            or alt_end.degrees < minimum_elevation_angle
        ):
            del satellite_list[i]
        else:
            i += 1
    print("Number of Satellites above the Horizon: ", i)
    if i == 0:
        raise Exception("No satellites above the horizon.")
    return satellite_list


def get_sat_orbits(
    reduced_sat_list: list[EarthSatellite],
    sim_time: float,
    sample_time: float,
    date_time: list[int],
    receiver_pos: list[float],
) -> Tuple[np.ndarray, list[str], list[datetime]]:
    """Get satellite orbits.

    Parameters
    ----------
    reduced_sat_list : list[EarthSatellite]
        _description_
    sim_time : float
        _description_
    sample_time : float
        _description_
    date_time : list[int]
        _description_
    receiver_pos : list[float]
        _description_

    Returns
    -------
    Tuple[np.ndarray, list[str], list[datetime]]
        _description_
    """
    # Initialization of start_time_datetime object using utc time zone
    start_time_datetime = datetime(*date_time, tzinfo=utc)  # type: ignore # NOTE: ignore unpacking `*` type error from `mypy`
    # Computation of the time series of datetime_objects with steps of 1 seconds with
    # the size of the user's input simulation time (sim_time)
    Samples_amount = int(sim_time / sample_time)
    timeseries_datetime = [
        start_time_datetime + timedelta(seconds=k * sample_time)
        for k in range(Samples_amount)
    ]
    # Initialization of the timescale
    ts = load.timescale()
    # Transforming the time series datetime object "timeseries_datetime"
    # to a timescale object.
    timeseries_utc = ts.from_datetimes(timeseries_datetime)
    # TODO: Implement also the dynamic receiver platform later.
    # Initialization of the receiver's position.
    receiver_pos = wgs84.latlon(*receiver_pos)  # type: ignore
    # Get a list of positions of each satellite using the receiver position as reference
    # This function iterates thorugh each satellite in "reduced_sat_list".
    # Each element of "relative_sat_receiver_pos" list is
    # of the type [Barycentric | Geocentric | ICRF].
    relative_sat_receiver_pos = [
        (sat - receiver_pos).at(timeseries_utc) for sat in reduced_sat_list
    ]
    # Initialize a list with the time series of altitude (elevation angle), azimuth and
    # distance objects for each satellites. Their elements permit to change unities
    # calling for specific methods.
    sat_pos_timeseries = np.zeros(
        (4, len(reduced_sat_list), Samples_amount), dtype=np.float64
    )
    sat_ids = []
    for sat in range(len(relative_sat_receiver_pos)):
        for timestep in range(Samples_amount):
            alt, az, dist = relative_sat_receiver_pos[sat][timestep].altaz()
            dist_rate = (
                relative_sat_receiver_pos[sat][timestep]
                .frame_latlon_and_rates(receiver_pos)[5]
                .m_per_s
            )
            sat_pos_timeseries[:, sat, timestep] = np.array(
                [alt.degrees, az.radians, dist.km, dist_rate]
            )
        sat_ids.append(reduced_sat_list[sat].name[2:])
    return sat_pos_timeseries, sat_ids, timeseries_datetime


def get_sats(
    date_time: list[int],
    receiver_pos: list[float],
    is_online: bool = True,
    is_cache_response: bool = True,
    satellite_system: Literal["gnss", "cubesat", "gps"] = "gnss",
    username: str = "rdlfresearch@gmail.com",
    password: str = "dustrodrigo15304931",
) -> list[EarthSatellite]:
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
    norad_ids = get_norad_ids(is_online, is_cache_response, satellite_system)
    tles = get_tles(
        norad_ids, date_time, username, password, is_online, is_cache_response
    )
    return _get_sat_over_horizon(_get_sats(tles), 600, date_time, receiver_pos, 5)
