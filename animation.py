import numpy as np
from matplotlib.animation import FuncAnimation
from constants import PLANETARY_DATA


def animate_frame(frame, planet_points):
    """Updates the positions of planets in orbit."""
    dt_days = 10
    current_time = frame * dt_days

    for planet, marker in planet_points.items():
        radius = PLANETARY_DATA[planet]["radius"]
        period_days = PLANETARY_DATA[planet]["period"]
        angle = 2 * np.pi * (current_time / period_days)
        marker.set_data([radius * np.cos(angle)], [radius * np.sin(angle)])

    return list(planet_points.values())


def start_animation(fig, planet_points):
    """Starts the orbital animation."""
    return FuncAnimation(fig, animate_frame, fargs=(planet_points,), frames=1000, interval=50, blit=False, repeat=True)
