"""_summary_."""

import matplotlib.pyplot as plt
import numpy as np


def skyplot_sat_orbit_timeseries(sat_pos_timeseries: np.array) -> None:
    """_summary_.

    Parameters
    ----------
    sat_pos_timeseries : np.array
    _description_
    """
    _, ax = plt.subplots()
    dimensions = sat_pos_timeseries.shape
    for sat in range(dimensions[1]):
        ax.plot(sat_pos_timeseries[3, sat, :])
    ax.grid(True)
    plt.show()
