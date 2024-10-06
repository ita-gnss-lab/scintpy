"""_summary_."""

import numpy as np


def skyplot_sat_orbit_timeseries(sat_pos_timeseries: np.array) -> None:
    """_summary_.

    Parameters
    ----------
    sat_pos_timeseries : np.array
        _description_
    """
    # _, ax = plt.subplots(subplot_kw={"projection": "polar"})
    # dimensions = sat_pos_timeseries.shape()
    # for sat in range(dimensions[1]):
    #        ax.plot(sat_pos_timeseries[1,sat,:],sat_pos_timeseries[0,sat,:])
    # ax.grid(True)
    # ax.set_rmax(90)  # Maximum radius corresponds to 90 degrees (zenith)
    # ax.set_rticks([30, 60, 90])  # Radial ticks (optional)
    # ax.set_rlabel_position(180)  # Position radial labels at 180 degrees
    # plt.show()
