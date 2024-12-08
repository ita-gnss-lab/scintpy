"""_summary_."""

from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import get_cmap

from .scenario import Scenario


def plot_sat_orbits(
    scenarios: Scenario | list[Scenario],
    reference_time: datetime,
) -> None:
    """Plot the satellite orbits and their respective velocities.

    Parameters
    ----------
    scenarios : Scenario | list[Scenario]
        An `Scenario` or a list of `Scenario` objects, where each element contains a
        receiver-satellite trajectory.
    reference_time: datetime
        The reference time used to search for the LOS satellites.
    """
    # Use a continuous colormap
    cmap = get_cmap("hsv")
    _, axs = plt.subplots(1, 2)
    axs[0].grid(True)
    axs[0].set_xlabel("Time (UTC)")
    axs[0].set_ylabel("Range Rate [m/s]")

    # Azimuth needs to be in radians for the polar plot
    # The polar plot assumes that the radius (elevation angle in this case)
    # always increase with respect to how far it is to the center.
    # Then, we need to plot the zenith angle instead of the elevation one.
    axs[1] = plt.subplot(1, 2, 2, projection="polar")
    axs[1].set_theta_offset(np.pi / 2)  # Offset by 90 degrees (pi/2 radians)
    axs[1].set_theta_direction(-1)
    axs[1].set_rticks([15, 30, 45, 60, 75, 90])
    axs[1].grid(True)

    if not isinstance(scenarios, list):
        scenarios = [scenarios]

    for i, scenario in enumerate(scenarios):
        # color code in the range [0, 1]
        color = cmap(i / len(scenarios))
        # [velocity x time] plot
        axs[0].plot(
            scenario.time.utc_datetime(),
            scenario.velocity_m_s,
            linewidth=2,
            label=scenario.satellite.name,
            color=color,
        )
        axs[0].legend()

        # sat orbit scatter plot
        # inital position
        axs[1].scatter(
            scenario.az_rad[0],
            90 - scenario.alt_deg[0],
            marker="o",
            color=color,
        )
        # # final position
        axs[1].scatter(
            scenario.az_rad[-1],
            90 - scenario.alt_deg[-1],
            marker="x",
            color=color,
        )
        # trajectory
        axs[1].plot(
            scenario.az_rad,
            90 - scenario.alt_deg,
            linewidth=2,
            color=color,
        )
        # # sat name annotation
        axs[1].text(
            scenario.az_rad[-1],
            90 - scenario.alt_deg[-1],
            f"{scenario.satellite.name}",
            fontsize=10,
            ha="center",
            va="bottom",
            color=color,
        )

    # reference time
    axs[0].axvline(
        reference_time,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Reference time",
    )
    plt.show()
