"""`tle_download module docstring."""

import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import requests
from requests.models import Response


def _handle_error(resp: Response) -> str:
    """Show the correct error message related to the status of the api request.

    Args:
        resp (datetime): response of the api

    Returns:
        error_message (str): error message to be shown
    """
    # Dictionary of common status codes and their meanings
    status_meanings: dict = {
        200: "OK - The request was successful.",
        201: "Created - A resource was created.",
        204: "No Content - The request was successful, but there is no content. Please, verify if the Date and Satellite ID selected are correct.",
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

    Args:
        start_date_str (str): start date and time in the format YYYY-MM-DD.

    Raises:
        e: shows an error in the case of a invalid start_date_str input format.

    Returns:
        end_date_str (str): Computed end date shifted by one day from the start date.
    """
    try:
        # Parse the input date (assuming it's in 'YYYY-MM-DD' format)
        start_date: datetime = datetime.strptime(start_date_str, "%Y-%m-%d")
        # Add one day using timedelta
        end_date: datetime = start_date + timedelta(days=1)
        # Format the result back to a string if needed
        end_date_str: str = end_date.strftime("%Y-%m-%d")
        return end_date_str
    except ValueError as e:
        # Print the error message and raise the exception to stop execution
        print("Error: Invalid date format. Please use the date formatting YYYY-MM-DD.")
        raise e  # Re-raise the exception to break the code


def _get_cache_file_path(filename: str) -> str:
    parent_dir = Path(__file__).resolve().parent.parent
    cached_file_path = parent_dir / "cached_data" / f"{filename}_response_text.txt"
    return str(cached_file_path)


# ??? why this name? should `get_sat_ids()` be more suitable?
def gnss_NORAD_ID_acquire(is_online: bool, is_cache_response: bool = False) -> str:
    """Acquire the list of actual operating GNSS satellites from celestrak website.

    Args:
        is_online (bool): `True`: Try to get a response from the online website `celestrak.org`. `False`: use the cached message.
        is_cache_response (bool): `True`: Save it (it will overwrite the previous `gp.txt` file). `False`: Don't save it. # ??? `gp.txt`?

    Raises:
        FileNotFoundError: Show the website error code and its meaning if something wrong occurs.

    Returns:
        ids (str): Comma-separated string with all operating GNSS satellittes NORAD catalog identification (NORAD_CAT_ID).
    """
    # path to the celestrak cached data .txt file
    celestrak_response_file_path: str = _get_cache_file_path("celestrak")
    # get a response from the online website `celestrak.org`
    if is_online:
        # request a tle list from celestrak website
        with requests.Session() as session:
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=gnss&FORMAT=3le"
            celestrak_resp: Response = session.get(url)
        # analyze the request get code
        if celestrak_resp.status_code != 200:
            error_message: str = _handle_error(celestrak_resp)
            raise Exception(error_message)
        celestrak_resp_text = celestrak_resp.text
        if is_cache_response:
            try:
                with open(celestrak_response_file_path, "w") as file:
                    cleaned_text = re.sub(r"\s*\r\n", r"\n", celestrak_resp_text)
                    file.write(cleaned_text)
            except FileNotFoundError as e:
                raise FileNotFoundError("Failed to save celestrak.org response") from e
    # use the cached message
    else:
        # try read the cached available .txt file
        try:
            with open(celestrak_response_file_path) as file:
                celestrak_resp_text = file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError("Failed to read the cached data file.") from e
    # match all NORAD satellite identifiers.
    matches: list[str] = re.findall(r"\n1 (\d+)", celestrak_resp_text)
    # comma-separated satellite IDs
    ids = ",".join(matches)
    return ids


def tle_request(
    sat_ids: str,
    date_time: tuple[int, int, int],
    username: str,
    password: str,
    is_online: bool,
    is_cache_response: bool = False,
) -> list[str]:
    """Obtain the raw TLE lines of all operating GNSS satellites from either the cached or online celestrak NORAD ID lists from the function gnss_NORAD_ID_acquire.

    Args:
        sat_ids (str): Comma-separed string of NORAD catalog ID of the satellite.
        date_time (list[int]): Start date and timing in 'Year,Month,Day,Hours,Minutes,Seconds' format.
        username (str): Username for space-track.org.
        password (str): Password for space-track.org.
        is_online (bool): `True`: Try to get a response from the `space-track.org`. `False`: Use the cached message file.
        is_cache_response (int): `True`: Chace the respose locally (it will overwrite the previous `space_track_response_file`). `False`: Don't save it.

    Raises:
        Exception: Shows errors related to unavailability of space-track api data service, not being able to find the space_track_response_text.txt file or invalid is_cache_response value.

    Returns:
        raw_tle_lines (list[str]): The TLE data in text format. Each element in the list is a line.
    """
    # cached file path
    space_track_response_file_path: str = _get_cache_file_path("space_track")
    # get a response from the online website `space-track.org`
    if is_online:
        # Ensure date_time has at least 3 elements
        if len(date_time) < 3:
            raise ValueError("Date time must contain at least year, month, and day.")
        general_date: datetime = datetime(*date_time[:3])
        start_date: str = general_date.strftime("%Y-%m-%d")
        # API base and TLE query endpoint
        uri_base = "https://www.space-track.org"
        request_login = "/ajaxauth/login"
        request_tle = f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{sat_ids}/orderby/TLE_LINE1%20ASC//EPOCH/{start_date}--{_get_end_date(start_date)}/format/3le/emptyresult/show"
        # Define login credentials directly
        site_cred = {"identity": username, "password": password}

        with requests.Session() as session:
            # Login to space-track.org
            space_track_resp: Response = session.post(
                uri_base + request_login, data=site_cred
            )
            # Fetch TLE data for the given satellite ID and date range
            space_track_resp = session.get(uri_base + request_tle)
            # Return the raw TLE text
        if space_track_resp.status_code != 200:
            error_message: str = _handle_error(space_track_resp)
            raise Exception(error_message)
        space_track_text = space_track_resp.text
        if is_cache_response:
            try:
                with open(space_track_response_file_path, "w") as file:
                    cleaned_text = re.sub(r"\s*\r\n", r"\n", space_track_text)
                    file.write(cleaned_text)
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    "Not able to cache response from space-track.org."
                ) from e
    # use cached message file
    else:
        try:
            with open(space_track_response_file_path) as file:
                space_track_text = file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError("Failed to read the cached data file.") from e
    raw_tle_lines: list[str] = space_track_text.splitlines()
    return raw_tle_lines


def group_raw_tle_lines(text: list[str]) -> tuple[tuple[str, str, str], ...]:
    """Creates a list with groups of three raw tle lines corresponding to each satellite ID requested to the API obtained from the function tle_request.

    Args:
        text (list[str]): Input TLE data as a string.

    Returns:
        tuple[list[str]]: A tuple of lists, each containing three lines of TLE data.
    """
    tle_list_size: int = len(text) // 3
    tle_list_tuple: tuple[tuple[str, str, str], ...] = tuple(
        (text[i * 3], text[i * 3 + 1], text[i * 3 + 2]) for i in range(tle_list_size)
    )
    return tle_list_tuple


def find_duplicates(
    tle_list_tuple: tuple[tuple[str, str, str], ...],
) -> defaultdict[str, list[tuple[str, str, str]]]:
    """_summary_.

    Args:
        tle_list_tuple (tuple[list[str], ...]): _description_.

    Returns:
        grouped_tle(defaultdict[list]): _description_.
    """
    grouped_tle: defaultdict[str, list[tuple[str, str, str]]] = defaultdict(list)

    # Group the tuples by the first element
    for tle in tle_list_tuple:
        identifier: str = tle[0]  # First element is the identifier
        grouped_tle[identifier].append(tle)
    return grouped_tle
