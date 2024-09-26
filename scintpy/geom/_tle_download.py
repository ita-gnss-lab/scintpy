"""`tle_download module docstring."""

import os
import re
from collections import defaultdict
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


def gnss_NORAD_ID_acquire(online_flag: int, save_api_response: int) -> str:
    """Acquire the list of actual operating GNSS satellites from celestrak website.

    Args:
        online_flag (int): Toggle offline celestrak.org response message for testing. 0 uses the offline message and 1 uses tries to get a response from the online website.
        save_api_response (int): Toggle saving the API response. set it as 0 to don't save it and 1 if you do want to save it. the saved file will overwrite the previous gp.txt file.

    Raises:
        Exception: shows the website error code and its meaning if something wrong occurs.

    Returns:
        id_str (str): string with all operating GNSS satellittes NORAD catalog identification (NORAD_CAT_ID) separated by commas
    """
    if online_flag == 1:
        with requests.Session() as session:
            url: str = (
                "https://celestrak.org/NORAD/elements/gp.php?GROUP=gnss&FORMAT=3le"
            )
            celestrak_resp: Response = session.get(
                url
            )  # Requests a tle list from celestrak website
        if celestrak_resp.status_code != 200:
            errorMessage: str = _handle_error(celestrak_resp)
            raise Exception(errorMessage)
        matches: list = re.findall(
            r"\n1 (\d+)", celestrak_resp.text.strip()
        )  # Finds all NORAD Satellite Identifiers.

        if save_api_response == 1:
            # finds the current directory path
            current_dir: str = os.path.dirname(os.path.abspath(__file__))
            # searches the path to the celestrak offline data .txt file
            celestrak_response_file_path: str = os.path.join(
                current_dir, "..", "offlineData", "celestrak_response_text.txt"
            )
            try:
                with open(celestrak_response_file_path, "w") as file:
                    cleaned_text: str = "\n".join(
                        [
                            line.strip()
                            for line in celestrak_resp.text.splitlines()
                            if line.strip()
                        ]
                    )  # Refactor the received text to write it into the .txt file correctly.
                    file.write(cleaned_text + "\n")
            except FileNotFoundError:
                print(f"File {celestrak_response_file_path} not found.")
        elif save_api_response != 0 or save_api_response != 1:
            raise Exception("Invalid save_api_response value")
    elif online_flag == 0:
        current_dir = os.path.dirname(
            os.path.abspath(__file__)
        )  # finds the current directory path
        celestrak_response_file_path = os.path.join(
            current_dir, "..", "offlineData", "celestrak_response_text.txt"
        )  # searches the path to the celestrak offline data .txt file
        try:
            with open(celestrak_response_file_path) as file:
                offline_celestrak_resp_text: str = (
                    file.read()
                )  # Reads the offline available .txt file.
        except FileNotFoundError:
            print(f"File {celestrak_response_file_path} not found.")
        matches = re.findall(
            r"\n1 (\d+)", offline_celestrak_resp_text
        )  # Finds all NORAD Satellite Identifiers.
    else:
        raise Exception("Invalid online_flag value")
    id_str = ",".join(matches)
    return id_str


def tle_request(
    sat_ids: str,
    dateTime: list[int],
    username: str,
    password: str,
    online_flag: int,
    save_api_response: int,
) -> list[str]:
    """Obtain the raw TLE lines of all operating GNSS satellites from either the offline or online celestrak NORAD ID lists from the function gnss_NORAD_ID_acquire.

    Args:
        sat_ids (str): NORAD catalog ID of the satellite.
        dateTime (list[int]): Start date and timing in 'Year,Month,Day,Hours,Minutes,Seconds' format.
        username (str): Username for space-track.org.
        password (str): Password for space-track.org.
        online_flag (int): Toggle offline space-track.org response message for testing. 0 uses the offline message and 1 uses tries to get a response from the online website.
        save_api_response (int): Toggle saving the API response. set it as 0 to don't save it and 1 if you do want to save it. the saved file will overwrite the previous space_track_response_file

    Raises:
        Exception: Shows errors related to unavailability of space-track api data service, not being able to find the space_track_response_text.txt file or invalid save_api_response value.

    Returns:
        raw_tle_lines (list[str]): The TLE data in text format or an empty string if the request fails.
    """
    if online_flag == 1:
        generalDate: datetime = datetime(dateTime[0], dateTime[1], dateTime[2])
        startDate: str = generalDate.strftime("%Y-%m-%d")
        # API base and TLE query endpoint
        uriBase: str = "https://www.space-track.org"
        requestLogin: str = "/ajaxauth/login"
        requestTLE: str = f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{sat_ids}/orderby/TLE_LINE1%20ASC//EPOCH/{startDate}--{_compute_end_date(startDate)}/format/3le/emptyresult/show"

        # Define login credentials directly
        siteCred: dict = {"identity": username, "password": password}

        with requests.Session() as session:
            # Login to space-track.org
            resp: Response = session.post(uriBase + requestLogin, data=siteCred)
            # Fetch TLE data for the given satellite ID and date range
            resp = session.get(uriBase + requestTLE)
            # Return the raw TLE text
        if resp.status_code != 200:
            errorMessage: str = _handle_error(resp)
            raise Exception(errorMessage)
        space_track_text = resp.text
        if save_api_response == 1:
            current_dir: str = os.path.dirname(os.path.abspath(__file__))
            celestrak_response_file_path: str = os.path.join(
                current_dir, "..", "offlineData", "space_track_response_text.txt"
            )
            try:
                with open(celestrak_response_file_path, "w") as file:
                    cleaned_text: str = "\n".join(
                        [
                            line.strip()
                            for line in space_track_text.splitlines()
                            if line.strip()
                        ]
                    )
                    file.write(cleaned_text + "\n")
            except FileNotFoundError:
                print(f"File {celestrak_response_file_path} not found.")
        elif save_api_response != 0 or save_api_response != 1:
            raise Exception("Invalid save_api_response value")
    elif online_flag == 0:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        celestrak_response_file_path = os.path.join(
            current_dir, "..", "offlineData", "space_track_response_text.txt"
        )
        try:
            with open(celestrak_response_file_path) as file:
                space_track_text = file.read()
        except FileNotFoundError:
            print(f"File {celestrak_response_file_path} not found.")
    else:
        raise Exception("Invalid online_flag value")
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
