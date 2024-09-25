"""`main.py` module docstring."""

import re

import geom.tle_download
import numpy as np

IDmatrix = geom.tle_download.gnss_NORAD_ID_acquire()
IDmatrix = np.array(IDmatrix)
sat_ids = ",".join(IDmatrix[:, 1])

dateTime = [2024, 8, 10, 12, 30, 00]  # YYYY, MM, DD, Hours, minutes, seconds
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

tles = geom.tle_download.tle_request(sat_ids, dateTime, username, password)
eachTle = tles.splitlines()
noradIdsAfter = re.findall(r"1 (\d{5})", tles)

# To find duplicates
seen = set()
duplicates = set()

for id in noradIdsAfter:
    if id in seen:
        duplicates.add(id)
    else:
        seen.add(id)

# Print duplicate IDs
if duplicates:
    print(f"Duplicate NORAD IDs found: {duplicates}")
else:
    print("No duplicate NORAD IDs found.")

bp = 1
