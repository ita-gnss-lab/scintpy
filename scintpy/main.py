from .geom.tleRequest import get_tle

sat_id = "24876"
date = "2023-09-10"
username = "rdlfresearch@gmail.com"
password = "dustrodrigo15304931"

tle: str = get_tle(sat_id, date, username, password)
print(tle)
