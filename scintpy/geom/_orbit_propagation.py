"""`_orbit_propagation.py` module docstring."""  # TODOC:

from datetime import datetime, timedelta

from skyfield.api import EarthSatellite, load, wgs84


def get_skyfield_sats(compact_tle_lines: list[str]) -> list[EarthSatellite]:
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


def get_sat_over_horizon(
    satellite_list: list[EarthSatellite],
    sim_time: float,
    date_time: list[int],
    receiver_pos_input: list[float],
) -> list[bool]:
    """Return a list with only those with line of sight.

    Parameters
    ----------
    satellite_list : list[EarthSatellite]
        Satellite list obtained from get_skyfield_sats function.
    sim_time : float
        Desired amount of time. # ??? in seconds?
    date_time : list[int]
        [Year,Month,Day,Hours,Minutes,seconds] list.
    receiver_pos_input : list[float]
        longitude [rad], latitude [rad] and height [m]

    Returns
    -------
    list[bool]
        # TODOC:
    """
    start_time_datetime = datetime(*date_time)  # type: ignore # NOTE: ignore unpacking `*` type error from `mypy`
    end_time_datetime = start_time_datetime + timedelta(seconds=sim_time)

    ts = load.timescale()
    start_time_utc = ts.utc(*date_time)  # type: ignore
    end_time_utc = ts.utc(
        end_time_datetime.year,
        end_time_datetime.month,
        end_time_datetime.day,
        end_time_datetime.hour,
        end_time_datetime.minute,
        end_time_datetime.second,
    )
    receiver_pos = wgs84.latlon(*receiver_pos_input)  # type: ignore
    del_list = []
    for sat in satellite_list:
        init_relative_pos = (sat - receiver_pos).at(start_time_utc)
        end_relative_pos = (sat - receiver_pos).at(end_time_utc)
        print(init_relative_pos.position.km[2], end_relative_pos.position.km[2])
        if init_relative_pos.position.km[2] < 0 or end_relative_pos.position.km[2] < 0:
            del_list.append(True)
        else:
            del_list.append(False)  # TODO: Finish later this function
    return del_list
