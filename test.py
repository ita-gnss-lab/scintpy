"""`test.py` module docstring."""

import numpy as np

import scintpy

IDmatrix: list | np.ndarray = scintpy.geom.gnss_NORAD_ID_acquire()
IDmatrix = np.array(IDmatrix)
sat_ids = ",".join(IDmatrix[:, 1])

dateTime = [2024, 8, 10, 12, 30, 00]  # YYYY, MM, DD, Hours, minutes, seconds
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

tles = scintpy.geom.tle_request(sat_ids, dateTime, username, password)
tles_list = scintpy.geom.post_process_tle_from_api(tles)

bp = 1
