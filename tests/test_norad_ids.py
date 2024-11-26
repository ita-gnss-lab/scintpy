"""Test the if the raw TLE response from `celestrak.org` is being handled correctly."""

from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture
from requests import Response


@pytest.mark.unit
def test_clean_raw_celestrak_response(mocker: MockerFixture) -> None:
    """Mock a `celestak.org` response and test whether its is correct."""
    # mock the response object
    mock_get_return = Mock(spec=Response)
    mock_get_return.status_code = 200
    mock_get_return.text = "GPS BIIR-2  (PRN 13)    \r\n1 24876U 97035A   24330.31981729  .00000070  00000+0  00000+0 0  9998\r\n2 24876  55.7269 120.8302 0085975  54.9372 305.8619  2.00561934200344\r\nGPS BIIR-4  (PRN 20)    \r\n1 26360U 00025A   24329.80330280 -.00000097  00000+0  00000+0 0  9993\r\n2 26360  54.7908  42.3480 0040035 222.6061 214.6812  2.00567413179856\r\nGPS BIIR-5  (PRN 22)    \r\n1 26407U 00040A   24329.71623462 -.00000039  00000+0  00000+0 0  9995\r\n2 26407  55.0052 237.7985 0139455 297.2393 274.4800  2.00562488178524\r\nGPS BIIR-8  (PRN 16)    \r\n1 27663U 03005A   24330.36058517 -.00000033  00000+0  00000+0 0  9994\r\n2 27663  55.0419 237.5840 0141062  48.4337  49.4750  2.00565749159903\r\nGPS BIIR-9  (PRN 21)    \r\n1 27704U 03010A   24330.50743885 -.00000083  00000+0  00000+0 0  9996\r\n2 27704  55.0608 347.2760 0257865 331.5949  87.8001  2.00568746158705\r\nGPS BIIR-11 (PRN 19)    \r\n1 28190U 04009A   24330.25269898 -.00000067  00000+0  00000+0 0  9996\r\n2 28190  55.3165 298.5961 0098566 155.2090  16.6069  2.00573384151538\r\n"  # noqa: E501

    # patch the requests.get method to return the mock response
    mocker.patch(
        "scintpy.geom._tle_download.requests.Session.get", return_value=mock_get_return
    )

    # NOTE: Import the function dynamically within the test so that the mock is in effect
    from scintpy.geom._tle_download import get_norad_ids

    ids: str = get_norad_ids(is_online=True, is_cache_response=False)

    assert all(
        id.isdigit() for id in ids.split(",")
    ), "All NORAD IDs from `celestrak.org` should be integer."

    assert all(
        len(id) == 5 for id in ids.split(",")
    ), "All NORAD IDs  from `celestrak.org` should contain 5 digits only."
