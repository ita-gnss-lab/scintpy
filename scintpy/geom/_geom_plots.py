"""_summary_."""

import matplotlib.pyplot as plt
import numpy as np


def plot_sat_orbits(sat_pos_timeseries: np.array, sat_ids: list[str]) -> None:
    """_summary_.

    Parameters
    ----------
    sat_pos_timeseries : np.array
    _description_
    """
    dimensions = sat_pos_timeseries.shape
    ax1 = plt.subplot(1, 2, 1)
    for sat in range(dimensions[1]):
        ax1.plot(sat_pos_timeseries[3, sat, :])

    ax2 = plt.subplot(1, 2, 2, projection="polar")
    # Azimuth needs to be in radians for the polar plot
    # The polar plot assumes that the radius (elevation angle in this case)
    # always increase with respect to how far it is to the center.
    # Then, we need to plot the zenith angle instead of the elevation one.
    for sat in range(dimensions[1]):
        ax2.plot(sat_pos_timeseries[1, sat, :], 90 - sat_pos_timeseries[0, sat, :])

    ax2.set_rticks([15, 30, 45, 60, 75, 90])
    ax2.grid(True)
    plt.show()
