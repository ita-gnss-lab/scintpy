"""`tle_download module docstring."""

import os
import re
from datetime import datetime, timedelta

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


def _compute_end_date(start_date_str: str) -> str:
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


def _get_response_file_path(filename: str) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rawtle_response_file_path = os.path.join(
        current_dir, "..", "offline_data", filename + "_response_text.txt"
    )
    return rawtle_response_file_path


# ??? why this name? should `get_sat_ids()` be more suitable?
def gnss_NORAD_ID_acquire(is_online: bool, is_save_response: bool = False) -> str:
    """Acquire the list of actual operating GNSS satellites from celestrak website.

    Args:
        is_online (bool): `True`: Try to get a response from the online website `celestrak.org`. `False`: use the cached message.
        is_save_response (bool): `True`: Save it (it will overwrite the previous `celestrak_response_text.txt` file). `False`: Don't save it.

    Raises:
        FileNotFoundError: Show the website error code and its meaning if something wrong occurs.

    Returns:
        ids (str): Comma-separated string with all operating GNSS satellittes NORAD catalog identification (NORAD_CAT_ID).
    """
    # path to the celestrak cached data .txt file
    celestrak_response_file_path: str = _get_response_file_path("celestrak")
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
        if is_save_response:
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
    matches: list = re.findall(r"\n1 (\d+)", celestrak_resp_text)
    # comma-separated satellite IDs
    ids = ",".join(matches)
    return ids


def tle_request(
    sat_ids: str,
    input_date: list[int],
    username: str,
    password: str,
    is_online: bool,
    is_save_response: bool,
) -> list[str]:
    """Obtain the raw TLE lines of all operating GNSS satellites from either the offline or online celestrak NORAD ID lists from the function gnss_NORAD_ID_acquire.

    Args:
        sat_ids (str): NORAD catalog ID of the satellite.
        input_date (list[int]): Start date and timing in 'Year,Month,Day,Hours,Minutes,Seconds' format.
        username (str): Username for space-track.org.
        password (str): Password for space-track.org.
        is_online (bool): Toggle offline space-track.org response message for testing. 0 uses the offline message and 1 uses tries to get a response from the online website.
        is_save_response (bool): Toggle saving the API response. set it as 0 to don't save it and 1 if you do want to save it. the saved file will overwrite the previous space_track_response_file

    Raises:
        Exception: Shows errors related to unavailability of space-track api data service, not being able to find the space_track_response_text.txt file or invalid is_save_response value.

    Returns:
        raw_tle_lines (list[str]): The TLE data in text format or an empty string if the request fails.
    """
    if is_online:
        user_date_input: datetime = datetime(
            input_date[0], input_date[1], input_date[2]
        )
        start_date: str = user_date_input.strftime("%Y-%m-%d")
        # API base and TLE query endpoint
        uri_base: str = "https://www.space-track.org"
        request_login: str = "/ajaxauth/login"
        request_tle: str = f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{sat_ids}/orderby/TLE_LINE1%20ASC//EPOCH/{start_date}--{_compute_end_date(start_date)}/format/3le/emptyresult/show"

        # Define login credentials directly
        siteCred: dict = {"identity": username, "password": password}

        with requests.Session() as session:
            # Login to space-track.org
            resp: Response = session.post(uri_base + request_login, data=siteCred)
            # Fetch TLE data for the given satellite ID and date range
            resp = session.get(uri_base + request_tle)
            # Return the raw TLE text
        if resp.status_code != 200:
            error_message: str = _handle_error(resp)
            raise Exception(error_message)
        space_track_text = resp.text
        if is_save_response == 1:
            space_track_response_file_path = _get_response_file_path("space_track")
            try:
                with open(space_track_response_file_path, "w") as file:
                    cleaned_text: str = "\n".join(
                        [
                            line.strip()
                            for line in space_track_text.splitlines()
                            if line.strip()
                        ]
                    )
                    file.write(cleaned_text + "\n")
            except FileNotFoundError:
                print(f"File {space_track_response_file_path} not found.")
    else:
        space_track_response_file_path = _get_response_file_path("space_track")
        try:
            with open(space_track_response_file_path) as file:
                space_track_text = file.read()
        except FileNotFoundError:
            print(f"File {space_track_response_file_path} not found.")
    raw_tle_lines: list[str] = space_track_text.splitlines()
    return raw_tle_lines


def tle_epoch_to_datetime(tle_epoch: str) -> datetime:
    """Convert a TLE epoch string (YYDDD.DDDDDD format) to a datetime object.

    Args:
        tle_epoch (str): TLE epoch in YYDDD.DDDDDD format where:
            - YY is the last two digits of the year.
            - DDD is the day of the year.
            - DDDDDD is the fractional part of the day.

    Returns:
        tle_datetime (datetime): A datetime object representing the TLE epoch.

    """
    year = int(tle_epoch[:2])  # First two digits are the year
    day_of_year = float(
        tle_epoch[2:]
    )  # Remaining part is day of the year (including fractional part)
    # Handle two-digit year (assumes 2000-2099; adjust if needed for different century)
    if year < 57:  # Convention: years < 57 are assumed to be in the 2000s
        year += 2000
    else:
        year += 1900
    # Calculate the base date from the year
    base_date = datetime(year, 1, 1)
    # Add the day of the year (minus 1 because January 1st is the 1st day)
    tle_datetime = base_date + timedelta(days=day_of_year - 1)
    return tle_datetime


def remove_duplicates(raw_tle_lines: list[str], date_time: list[int]) -> list[str]:
    """This function receives the raw tle lines from tle_request function and removes its duplicated tles, keeping only the tles with the minor absolute difference between the user's input date and time and its epoch.

    Args:
        raw_tle_lines (list[str]): raw tle lines from tle_request function
        date_time (list[int]): user's input date and time

    Returns:
        list[str]: compacted version of the tle lines without the duplicates.
    """
    user_date_input = datetime(
        date_time[0],
        date_time[1],
        date_time[2],
        date_time[3],
        date_time[4],
        date_time[5],
    )
    current_id = ""
    current_epoch = ""
    previous_id = ""
    previous_epoch = ""
    tle_discard_list = []
    for i in range(len(raw_tle_lines) // 3):
        if i == 0:
            previous_id = raw_tle_lines[i * 3]
            previous_epoch = raw_tle_lines[i * 3 + 1][18:32]
            abs_previous_time_diff = abs(
                user_date_input - tle_epoch_to_datetime(previous_epoch)
            )
        else:
            current_id = raw_tle_lines[i * 3]
            current_epoch = raw_tle_lines[i * 3 + 1][18:32]
            abs_current_time_diff = abs(
                user_date_input - tle_epoch_to_datetime(current_epoch)
            )
            if current_id == previous_id:
                if abs_current_time_diff <= abs_previous_time_diff:
                    tle_discard_list.append(
                        [(i - 1) * 3, (i - 1) * 3 + 1, (i - 1) * 3 + 2]
                    )
                else:
                    tle_discard_list.append([i * 3, i * 3 + 1, i * 3 + 2])
            previous_id = current_id
            abs_previous_time_diff = abs_current_time_diff
    formatted_tle_discard_list = [
        index for minor_list_number in tle_discard_list for index in minor_list_number
    ]
    for index in sorted(formatted_tle_discard_list, reverse=True):
        del raw_tle_lines[index]
    compact_tle_lines = raw_tle_lines
    return compact_tle_lines
