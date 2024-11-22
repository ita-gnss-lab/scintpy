"""_summary_."""

from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np


def plot_sat_orbits(
    sat_pos_timeseries: np.array, sat_ids: list[str], datetime_ts: list[datetime]
) -> None:
    """_summary_.

    Parameters
    ----------
    sat_pos_timeseries : np.array
    _description_
    """
    dimensions = sat_pos_timeseries.shape
    color_values = plt.cm.viridis(np.arange(0, 1, 1 / dimensions[1]))
    ax1 = plt.subplot(1, 2, 1)
    for sat in range(dimensions[1]):
        ax1.plot(
            datetime_ts,
            sat_pos_timeseries[3, sat, :],
            linewidth=2,
            color=color_values[sat],
        )
    ax1.legend(sat_ids)
    ax1.grid(True)
    ax1.set_xlabel("Time (UTC) [sec]")
    ax1.set_ylabel("Range Rate [m/s]")

    # Azimuth needs to be in radians for the polar plot
    # The polar plot assumes that the radius (elevation angle in this case)
    # always increase with respect to how far it is to the center.
    # Then, we need to plot the zenith angle instead of the elevation one.
    ax2 = plt.subplot(1, 2, 2, projection="polar")
    ax2.set_theta_offset(np.pi / 2)  # Offset by 90 degrees (pi/2 radians)
    ax2.set_theta_direction(-1)
    for sat in range(dimensions[1]):
        ax2.scatter(
            sat_pos_timeseries[1, sat, 0],
            90 - sat_pos_timeseries[0, sat, 0],
            marker="o",
            color=color_values[sat],
        )
        ax2.scatter(
            sat_pos_timeseries[1, sat, -1],
            90 - sat_pos_timeseries[0, sat, -1],
            marker="x",
            color=color_values[sat],
        )
        ax2.plot(
            sat_pos_timeseries[1, sat, :],
            90 - sat_pos_timeseries[0, sat, :],
            linewidth=1,
            color=color_values[sat],
        )
        ax2.text(
            sat_pos_timeseries[1, sat, -1],
            90 - sat_pos_timeseries[0, sat, -1],
            f"{sat_ids[sat]}",
            fontsize=10,
            ha="center",
            va="bottom",
            c=color_values[sat],
        )
    ax2.set_rticks([15, 30, 45, 60, 75, 90])
    ax2.grid(True)
    plt.show()
