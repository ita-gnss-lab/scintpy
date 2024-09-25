"""`tle_request` module docstring."""

from datetime import datetime, timedelta

import requests


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


def process_tle_data(tle_data):
    """_summary_.

    Args:
        tle_data (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Split the TLE into individual lines
    tle_lines = tle_data.strip().split("\n")

    # Assuming TLEs are given in pairs (two lines per TLE), group them
    tles = [(tle_lines[i], tle_lines[i + 1]) for i in range(0, len(tle_lines), 2)]

    # You can add logic here to filter TLEs based on specific criteria.
    # For example, we can choose the last TLE (most recent) for simplicity:
    chosen_tle = tles[-1]  # This picks the last TLE

    return chosen_tle


def tle_request(sat_id, date, username, password):
    """Fetch TLE data for a given satellite ID within a start and end date range using the TLE format.

    Args:
        sat_id (str): NORAD catalog ID of the satellite.
        date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        username (str): Username for space-track.org.
        password (str): Password for space-track.org.

    Raises:
        Exception: _description_

    Returns:
        str: The TLE data in text format or an empty string if the request fails.
    """
    # API base and TLE query endpoint
    uriBase = "https://www.space-track.org"
    requestLogin = "/ajaxauth/login"
    requestTLE = f"/basicspacedata/query/class/gp_history/NORAD_CAT_ID/{sat_id}/orderby/TLE_LINE1%20ASC/EPOCH/{date}--{compute_end_date(date)}/format/tle"

    # Define login credentials directly
    siteCred = {"identity": username, "password": password}

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


def get_tle(sat_id: str, date: str, username: str, password: str) -> str:
    """_summary_.

    Args:
        sat_id (str): _description_
        date (str): _description_
        username (str): _description_
        password (str): _description_

    Returns:
        str: _description_
    """
    downlodaded_tle = tle_request(sat_id, date, username, password)
    chosen_tle = process_tle_data(downlodaded_tle)
    return chosen_tle
