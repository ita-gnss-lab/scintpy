"""`main.py` module docstring."""

import geom.tle_download
import numpy as np

IDmatrix = geom.tle_download.gnss_NORAD_ID_acquire()
IDmatrix = np.array(IDmatrix)
sat_ids = ",".join(IDmatrix[:, 1])

dateTime = [2024, 8, 10, 12, 30, 00]  # YYYY, MM, DD, Hours, minutes, seconds
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

tles = geom.tle_download.tle_request(sat_ids, dateTime, username, password)
tles_list = geom.tle_download.post_process_tle_from_api(tles)

bp = 1
