"""`tle_download module docstring."""

import re
from datetime import datetime, timedelta

import requests
from requests.models import Response


def handle_error(resp):
    """_summary_.

    Args:
        resp (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Dictionary of common status codes and their meanings
    status_meanings = {
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
    status_message = status_meanings.get(resp.status_code, "Unknown error occurred")
    # Present a better error message
    return f"Error {resp.status_code}: {status_message}"


def compute_end_date(start_date_str):
    """Compute the next day of the calendar for the space-track website request.

    Args:
        start_date_str (_type_): _description_

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """
    try:
        # Parse the input date (assuming it's in 'YYYY-MM-DD' format)
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        # Add one day using timedelta
        end_date = start_date + timedelta(days=1)
        # Format the result back to a string if needed
        return end_date.strftime("%Y-%m-%d")
    except ValueError as e:
        # Print the error message and raise the exception to stop execution
        print("Error: Invalid date format. Please use 'YYYY-MM-DD'.")
        raise e  # Re-raise the exception to break the code


def gnss_NORAD_ID_acquire() -> list[list]:
    """Get all current operating GNSS satellites available at Celestrak website.

    Args:
        empty

    Raises:
        e: _description_

    Returns:
        IDmatrix (str): Matrix with two rows corresponding to the satellite name and NORAD_CAT_ID respectively.
    """
    with requests.Session() as session:
        url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=gnss&FORMAT=3le"
        celestrak_resp: Response = session.get(url)

    if celestrak_resp.status_code != 200:
        errorMessage = handle_error(celestrak_resp)
        raise Exception(errorMessage)
    else:
        matches: list[tuple] = re.findall(r"(\S+.*)\r\n1 (\d+)", celestrak_resp.text)
        IDmatrix: list[list] = [[match[0], match[1]] for match in matches]
        return IDmatrix


def tle_request(sat_ids: str, date: list[int], username: str, password: str) -> str:
    """Fetch TLE data for a given satellite ID within a start and end date range using the TLE format.

    Args:
        sat_ids (str): NORAD catalog ID of the satellite.
        date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        username (str): Username for space-track.org.
        password (str): Password for space-track.org.

    Raises:
        Exception: _description_

    Returns:
        str: The TLE data in text format or an empty string if the request fails.
    """
    generalDate: datetime = datetime(
        date[0], date[1], date[2], date[3], date[4], date[5]
    )
    startDate: str = generalDate.strftime("%Y-%m-%d")
    # API base and TLE query endpoint
    uriBase: str = "https://www.space-track.org"
    requestLogin: str = "/ajaxauth/login"
    requestTLE: str = f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{sat_ids}/EPOCH/{startDate}--{compute_end_date(startDate)}/format/tle/distinct/true/emptyresult/show"

    # Define login credentials directly
    siteCred: dict = {"identity": username, "password": password}

    with requests.Session() as session:
        # Login to space-track.org
        resp = session.post(uriBase + requestLogin, data=siteCred)
        # Fetch TLE data for the given satellite ID and date range
        resp = session.get(uriBase + requestTLE)
        # Return the raw TLE text
    if resp.status_code != 200:
        errorMessage = handle_error(resp)
        raise Exception(errorMessage)
    return resp.text
