import numpy as np
from constants import PLANETARY_DATA


def calculate_hohmann_transfer_time(departure, destination):
    """Calculates the estimated Hohmann transfer time in days."""
    if departure not in PLANETARY_DATA or destination not in PLANETARY_DATA:
        raise ValueError("Invalid planet name!")

    if departure == destination:
        return 0

    r1 = PLANETARY_DATA[departure]["radius"]
    r2 = PLANETARY_DATA[destination]["radius"]

    trip_time_years = np.pi * np.sqrt(((r1 + r2) ** 3) / (8 * 1.0))
    return round(trip_time_years * 365, 1)
