"""`tle_download module docstring."""  # TODOC:

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

import requests
from loguru import logger
from requests.exceptions import HTTPError
from requests.models import Response


def _tle_epoch_to_datetime(tle_epoch: str) -> datetime:
    """Convert a TLE epoch string (YYDDD.DDDDDD format) to a datetime object.

    Parameters
    ----------
    tle_epoch : str
        TLE epoch in YYDDD.DDDDDD format where:
            - YY is the last two digits of the year.
            - DDD is the day of the year.
            - DDDDDD is the fractional part of the day.

    Returns
    -------
    datetime
        A datetime object representing the TLE epoch.
    """
    # first two digits are the year
    year = int(tle_epoch[:2])
    # remaining part is day of the year (including fractional part)
    day_of_year = float(tle_epoch[2:])
    # handle two-digit year (assumes 2000-2099; adjust if needed for different century)
    if year < 57:  # NOTE: convention: years < 57 are assumed to be in the 2000s
        year += 2000
    else:
        year += 1900
    # get the base date from the year
    base_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    # add the day of the year (minus 1 because January 1st is the 1st day)
    tle_datetime = base_date + timedelta(days=day_of_year - 1)
    return tle_datetime


def _handle_error(resp: Response) -> str:
    """Show the correct error message related to the status of the api request.

    Parameters
    ----------
    resp : Response
        Response of the API.

    Returns
    -------
    str
        Error message to be shown.
    """
    # Dictionary of common status codes and their meanings
    status_meanings: dict = {
        200: "OK - The request was successful.",
        201: "Created - A resource was created.",
        204: (
            "No Content - The request was successful, but there is no content."
            "Please, verify if the Date and Satellite ID selected are correct."
        ),
        400: "Bad Request - The request was invalid.",
        401: "Unauthorized - Authentication failed.",
        403: "Forbidden - You do not have permission.",
        404: "Not Found - The resource could not be found.",
        500: "Internal Server Error - The server encountered an error.",
        502: "Bad Gateway - Invalid response from the upstream server.",
        503: "Service Unavailable - The server is overloaded or down.",
        504: "Gateway Timeout - The server timed out waiting for the upstream server.",
    }
    # Get the status code meaning, default to a generic message if unknown
    status_message: str = status_meanings.get(
        resp.status_code, "Unknown error occurred"
    )
    # Present a better error message
    error_message: str = f"Error {resp.status_code}: {status_message}"
    return error_message


def _get_end_date(start_date_str: str) -> str:
    """Compute the next day of the calendar for the space-track website request.

    Parameters
    ----------
    start_date_str : str
        Start date and time in the format YYYY-MM-DD.

    Returns
    -------
    str
        End date and time in the format YYYY-MM-DD.

    Raises
    ------
    ValueError
        Invalid date format.
    """
    try:
        # parse the input date (assuming it's in 'YYYY-MM-DD' format)
        start_date: datetime = datetime.strptime(start_date_str, "%Y-%m-%d")
        # add one day using timedelta
        end_date: datetime = start_date + timedelta(days=1)
        # format the result back to a string if needed
        end_date_str: str = end_date.strftime("%Y-%m-%d")
        return end_date_str
    except ValueError as e:
        # print the error message and raise the exception to stop execution
        raise ValueError(
            "Error: Invalid date format. Please use the date formatting YYYY-MM-DD."
        ) from e


def _get_cache_file_path(filename: str, satellite_system: str) -> str:
    """Return relative file path to cached data.

    Parameters
    ----------
    filename : str
        Filename (with the extension) of the cached data.
    satellite_system : str
        The satellite type that `scintpy` should search for.

    Returns
    -------
    str
        Relative file path.
    """
    parent_dir = Path(__file__).resolve().parent
    cached_file_path = (
        parent_dir / "cached_data" / f"{filename}_response_{satellite_system}_text.txt"
    )
    return str(cached_file_path)


def _remove_duplicates(raw_tle_lines: list[str], reference_time: datetime) -> list[str]:
    """Get raw tle lines and return new tle lines with duplicates removed.

    Some TLE requests may contain more than one timestamp for a same NORAD ID. This
    function returns a list with the duplicates removed, leaving only the closest
    epoch with respect to `reference_time`.

    Parameters
    ----------
    raw_tle_lines : list[str]
        Raw TLE lines, possibly with duplicates.
    reference_time : datetime
        UTC reference time from where `scintpy` searches for satellites whose
        observation window contains `reference_time`.

    Returns
    -------
    list[str]
        New TLE lines with duplicates removed, keeping only the tles with the minor
        absolute difference between the user's input date and time and its epoch.
    """
    i = 0
    # as long as there is a next satellite to select
    while 3 * (i + 1) < len(raw_tle_lines):
        current_id = raw_tle_lines[3 * i]
        next_id = raw_tle_lines[3 * (i + 1)]

        # same satellite, compare epoch difference with respect to `date_time`
        if current_id == next_id:
            # time difference between the current satellite epoch and `date_time`
            current_epoch = raw_tle_lines[3 * i + 1][18:32]
            abs_current_time_diff = abs(
                reference_time - _tle_epoch_to_datetime(current_epoch)
            )
            # time difference between the next satellite epoch and `date_time`
            next_epoch = raw_tle_lines[3 * (i + 1) + 1][18:32]
            abs_next_time_diff = abs(
                reference_time - _tle_epoch_to_datetime(next_epoch)
            )

            # current satellite epoch is closer to `date_time`: delete next satellite
            if abs_current_time_diff < abs_next_time_diff:
                del raw_tle_lines[3 * (i + 1) : 3 * (i + 1) + 3]
            # next satellite epoch is closer to `date_time`: delete current satellite
            else:
                del raw_tle_lines[3 * i : 3 * i + 3]
        # different satellites, go to next
        else:
            i += 1

    compact_tle_lines = raw_tle_lines
    return compact_tle_lines


def get_norad_ids(
    is_online: bool,
    is_cache_response: bool,
    satellite_system: Literal["gnss", "cubesat", "gps"],
) -> str:
    """Return the list of the operating satellite NORAD IDs from `celestrak.org`.

    `celestrak.org` returns the real-time TLEs of active satellites, being not possible
     to request TLEs in the past. Therefore, only the NORAD IDs for a given satellite
     system are returned. These IDs are used afterwards to request the TLEs at the
     desired datetime on `space-track.org`.

    Parameters
    ----------
    is_online : bool
        `True`: Try to get a response from the online website `celestrak.org`; `False`:
        Use the cached message.
    is_cache_response : bool, optional
        `True`: Save overwriting previous cached data (it implies that `is_online` is
        `True`); `False`: Don't cached it.
    satellite_system: str
        The satellite type that `scintpy` should search for. By default "gnss".

    Returns
    -------
    str
        Comma-separated string with all operating satellittes NORAD catalog
        identification (NORAD_CAT_ID).

    Raises
    ------
    KeyError
        Invalid satellite system.
    HTTPError
        GET resquest error.
    FileNotFoundError
        Failed to save celestrak.org response.
    FileNotFoundError
        Failed to read the cached data file.
    """
    # path to the celestrak cached data .txt file
    celestrak_response_file_path: str = _get_cache_file_path(
        "celestrak", satellite_system
    )
    # get a response from the online website `celestrak.org`
    if is_online:
        # get URL
        satellite_systems = {
            "gnss": "https://celestrak.org/NORAD/elements/gp.php?GROUP=gnss&FORMAT=3le",
            "cubesat": "https://celestrak.org/NORAD/elements/gp.php?GROUP=cubesat&FORMAT=3le",
            "gps": "https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=3le",
        }
        url = satellite_systems[satellite_system]
        if not url:
            raise KeyError("Invalid satellite system.")

        # request a tle list from `celestrak.org`
        with requests.Session() as session:
            celestrak_resp: Response = session.get(url)
        # analyze the request get code
        if celestrak_resp.status_code != 200:
            error_message: str = _handle_error(celestrak_resp)
            raise HTTPError(error_message)
        logger.debug("Successful NORAD IDs GET request from `celestrak.org`.")
        celestrak_resp_text = celestrak_resp.text
        cleaned_text = re.sub(r"\s*\r\n", r"\n", celestrak_resp_text)

        assert len(cleaned_text) <= len(
            celestrak_resp_text
        ), "Raw response from `celestrak.org` was not been cleaned correctly"

        if is_cache_response:
            try:
                with open(celestrak_response_file_path, "w") as file:
                    file.write(cleaned_text)
                    logger.debug(
                        "NORAD IDs have been successfully cached "
                        f"in  {celestrak_response_file_path}."
                    )
            except FileNotFoundError as e:
                raise FileNotFoundError("Failed to save celestrak.org response.") from e
    # use the cached message
    else:
        # try read the cached available .txt file
        try:
            with open(celestrak_response_file_path) as file:
                cleaned_text = file.read()
            logger.debug(
                "NORAD IDs have been successfully read from the "
                f"cached file in {celestrak_response_file_path}."
            )
        except FileNotFoundError as e:
            raise FileNotFoundError("Failed to read the cached data file.") from e
    # match all NORAD satellite identifiers.
    matches: list[str] = re.findall(r"\n1 (\d+)", cleaned_text)
    logger.trace(f"{len(matches)} NORAD IDs are being used.")
    # comma-separated satellite IDs
    ids = ",".join(matches)
    return ids


def get_tles(
    norad_ids: str,
    reference_time: datetime,
    username: str,
    password: str,
    is_online: bool,
    is_cache_response: bool,
    satellite_system: str,
) -> list[str]:
    """Get TLE lines from `space-track.org` for a given set of NORAD IDs at a datetime.

    The NORAD IDs were either previously cached to requested from `celestrak.org` and
    are tailored to a certain type of satellites.

    Parameters
    ----------
    norad_ids : str
        Comma-separated string of NORAD catalog ID of the satellite.
    reference_time : datetime
        UTC reference time from where `scintpy` searches for satellites whose
        observation window contains `reference_time`.
    username : str
        The username used to request data on `space-track.org`. It is used if and only
        if `is_online` is `True`.
    password : str
        The password used to request data on `space-track.org`. It is used if and only
        if `is_online` is `True`
    is_online : bool
        `True`: Try to get a response from the `space-track.org`; `False`: Use the
        cached message file.
    is_cache_response : bool, optional
        Save overwriting previous cached data (It implies that `is_online` is
        `True`); `False`: Don't cached it.

    Returns
    -------
    list[str]
        The TLE data in text format. Each element in the list is a line.

    Raises
    ------
    HTTPError
        GET or POST resquest error from space-track api data service.
    FileNotFoundError
        Not able to cache response from space-track.org.
    FileNotFoundError
        Failed to read the cached data file.
    """
    # cached file path
    space_track_response_file_path: str = _get_cache_file_path(
        "space_track", satellite_system
    )
    # get a response from the online website `space-track.org`
    if is_online:
        start_date: str = reference_time.strftime("%Y-%m-%d")
        # API base and TLE query endpoint
        uri_base = "https://www.space-track.org"
        request_login = "/ajaxauth/login"
        request_tle = (
            f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{norad_ids}"
            f"/orderby/TLE_LINE1%20ASC//EPOCH/{start_date}--{_get_end_date(start_date)}"
            "/format/3le/emptyresult/show"
        )
        # define login credentials directly
        site_cred = {"identity": username, "password": password}

        with requests.Session() as session:
            # login to space-track.org
            space_track_resp: Response = session.post(
                uri_base + request_login, data=site_cred
            )
            # letch TLE data for the given satellite ID and date range
            space_track_resp = session.get(uri_base + request_tle)
            # return the raw TLE text
        if space_track_resp.status_code != 200:
            error_message: str = _handle_error(space_track_resp)
            raise HTTPError(error_message)
        logger.debug("Successful TLEs GET request from `space-track.org`.")
        space_track_text = space_track_resp.text
        if is_cache_response:
            try:
                with open(space_track_response_file_path, "w") as file:
                    cleaned_text = re.sub(r"\s*\r\n", r"\n", space_track_text)
                    assert len(cleaned_text) < len(
                        space_track_text
                    ), "`space-track.org` response is not being cleaned properly."
                    file.write(cleaned_text)
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    "Not able to cache response from `space-track.org`."
                ) from e
            logger.debug(
                "NORAD IDs have been successfully cached "
                f"in  {space_track_response_file_path}."
            )
    # use cached message file
    else:
        try:
            with open(space_track_response_file_path) as file:
                space_track_text = file.read()
                logger.debug(
                    "TLEs have been successfully read from the "
                    f"cached file in {space_track_response_file_path}."
                )
        except FileNotFoundError as e:
            raise FileNotFoundError("Failed to read the cached data file.") from e
    raw_tle_lines: list[str] = space_track_text.splitlines()
    return _remove_duplicates(raw_tle_lines, reference_time)
