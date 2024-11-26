"""Test the if the raw TLE response from `space-track.org` is handled correctly."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from requests import Response, Session


def _mock_session() -> MagicMock:
    """Mock session and response in a unit test."""
    # create a mock for the requests session
    mock_session = MagicMock(spec=Session)

    # Mock `__enter__` and `__exit__` for context manager behavior
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    # mock `post()` return
    mock_post_return = MagicMock(spec=Response)
    mock_post_return.status_code = 200  # NOTE: 200 for success

    # mock `get()` return
    mock_get_return = MagicMock(spec=Response)
    mock_get_return.status_code = 200  # NOTE: 200 for success
    mock_get_return.text = "0 NAVSTAR 43 (USA 132)\r\n1 24876U 97035A   24302.39915371  .00000082  00000-0  00000+0 0  9999\r\n2 24876  55.7149 121.9219 0085478  54.7594 306.0903  2.00561667199789\r\n0 NAVSTAR 43 (USA 132)\r\n1 24876U 97035A   24302.39915371  .00000082  00000-0  00000-0 0  9990\r\n2 24876  55.7149 121.9219 0085478  54.7594 306.0903  2.00561667199981\r\n0 NAVSTAR 43 (USA 132)\r\n1 24876U 97035A   24302.89773807  .00000082  00000-0  00000-0 0  9991\r\n2 24876  55.7152 121.9024 0085492  54.7671 306.0822  2.00561669199994\r\n0 NAVSTAR 47 (USA 150)\r\n1 26360U 00025A   24302.01239243 -.00000089  00000-0  00000-0 0  9997\r\n2 26360  54.7713  43.4781 0039809 220.0395 310.3282  2.00569476179299\r\n0 NAVSTAR 48 (USA 151)\r\n1 26407U 00040A   24302.49747413 -.00000049  00000-0  00000+0 0  9996\r\n2 26407  55.0170 238.8805 0140960 296.6575  61.8162  2.00562089177970\r\n0 NAVSTAR 48 (USA 151)\r\n1 26407U 00040A   24302.49747413 -.00000049  00000-0  00000-0 0  9997\r\n2 26407  55.0170 238.8805 0140960 296.6575  61.8162  2.00562089177981\r\n0 NAVSTAR 51 (USA 166)\r\n1 27663U 03005A   24302.53555285 -.00000049  00000-0  00000+0 0  9994\r\n2 27663  55.0542 238.6902 0139702  48.0742 118.4102  2.00567274159335\r\n"  # noqa: E501

    # mock POST request
    mock_session.post.return_value = mock_post_return
    # mock GET request
    mock_session.get.return_value = mock_get_return

    return mock_session


@pytest.mark.unit
def test_tles_celestrak_response(mocker: MockerFixture) -> None:
    """Mock a `space-track.org` response and test whether its is correct."""
    # mock the `requests.Session` instance
    mock_Session_return = _mock_session()

    # patch the requests.get method to return the mock response
    mocker.patch(
        "scintpy.geom._tle_download.requests.Session", return_value=mock_Session_return
    )

    # NOTE: Import the function dynamically within the test so that the mock is in effect
    from scintpy.geom._tle_download import get_tles

    all_sat_sys = {
        "BEIDOU",
        "LUCH",
        "GALAXY",
        "COSMOS",
        "GSAT",
        "IRNSS",
        "GALILEO",
        "QZS-4",
        "QZS-1R",
        "BD-20",
        "INMARSAT",
        "ANIK",
        "BEIDOU-3",
        "NAVSTAR",
        "SES",
        "BD-2-G7",
        "ASTRA",
        "QZS-3",
        "NVS-01",
    }

    mock_norad_ids = "24876,26360,26407,27663,27704,28190,28474,28868,28874,28899,29486,29601,32260,32275,32276,32384,32393,32395,32711,35752,36111,36112,36402,36585,36828,37210,37256,37384,37605,37763,37846,37847,37867,37868,37869,37948,37951,38091,38250,38251,38652,38775,38779,38833,38857,38953,38977,39155,39166,39199,39533,39617,39620,39635,39727,39741,40001,40105,40128,40129,40269,40294,40315,40534,40544,40545,40547,40549,40730,40748,40749,40889,40890,40938,41019,41028,41174,41175,41241,41328,41330,41384,41434,41469,41549,41550,41586,41589,41859,41860,41861,41862,42709,42738,42917,42939,42965,43001,43002,43055,43056,43057,43058,43107,43108,43207,43208,43245,43246,43286,43508,43539,43564,43565,43566,43567,43581,43582,43602,43603,43622,43623,43647,43648,43683,43687,43706,43707,43873,44204,44231,44299,44337,44506,44542,44543,44709,44793,44794,44850,44864,44865,45344,45358,45807,45854,46114,46805,46826,48859,49336,49809,49810,52984,54031,54377,55268,56564,56759,57517,58654,58655,59598,59600,61182,61183"  # noqa: E501

    # patch the requests.get method to return the mock response
    mock_date_time = [2024, 10, 28, 8, 54, 0]
    mock_username = "rdlfresearch@gmail.com"
    mock_password = "dustrodrigo15304931"

    tles: list[str] = get_tles(
        mock_norad_ids, mock_date_time, mock_username, mock_password, True
    )

    assert all(
        sat_sys in all_sat_sys for sat_sys in [tle.split()[1] for tle in tles[::3]]
    ), "All sat systems are not in their correct position"
