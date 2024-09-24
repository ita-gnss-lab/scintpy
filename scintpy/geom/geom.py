from skyfield.api import Loader

name = "gnss.csv"  # File Name

base = "https://celestrak.org/NORAD/elements/gp.php"  # base celestrak website
url = (
    base + "?INTDES=1997-035&FORMAT=tle"
)  # Aiming GNSS satellite orbits files with csv format
load_ = Loader(
    "scintpy/skyfield-data"
)  # Sets the data directory to keep everything organized  # noqa: F811
load_.download(url, filename=name)  # Downloads all gnss available orbits
# type: ignore
