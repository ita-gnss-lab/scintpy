"""_summary_."""

import scintpy

date_time = [2024, 10, 28, 8, 54, 0]  # [2024, 10, 5, 9, 10, 20]
# São José dos Campos
receiver_pos = [-23.20713241666, -45.861737777, 605.088]

sat = scintpy.geom.get_sats(date_time, receiver_pos)
