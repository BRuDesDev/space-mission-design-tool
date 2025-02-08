from mission_calculations import calculate_hohmann_transfer_time
from animation import start_animation
from constants import LOGO_PATH, LOGO_WIDTH, LOGO_HEIGHT, PLANETARY_DATA

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import os
from PIL import Image, ImageTk


class SpaceMissionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Mission Main Window")
        self.root.geometry("600x500")

        self.logo_img = None

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Select Departure Planet:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.departure_entry = ttk.Entry(main_frame, width=30)
        self.departure_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(main_frame, text="Select Destination Planet:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.destination_entry = ttk.Entry(main_frame, width=30)
        self.destination_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        calc_button = ttk.Button(main_frame, text="Calculate Mission", command=self.calculate_mission)
        calc_button.grid(row=3, column=1, pady=10, sticky="w")

        self.trip_label = ttk.Label(main_frame, text="Trip Length: --", font=("Arial", 12, "bold"))
        self.trip_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Initialize variables for plot window
        self.plot_window = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.toolbar = None
        self.planet_points = {}

        # Load and display the logo
        self.load_logo(main_frame)

    def load_logo(self, parent):
        """Load and resize the logo, placing it in the GUI."""
        try:
            if not os.path.exists(LOGO_PATH):
                raise FileNotFoundError(f"Logo not found at {LOGO_PATH}")

            original_logo = Image.open(LOGO_PATH)
            resized_logo = original_logo.resize((LOGO_WIDTH, LOGO_HEIGHT), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(resized_logo)  # Store reference

            logo_label = ttk.Label(parent, image=self.logo_img)
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        except Exception as e:
            messagebox.showwarning("Logo Warning", f"Could not load logo: {e}")

    def calculate_mission(self):
        departure = self.departure_entry.get().strip().title()
        destination = self.destination_entry.get().strip().title()

        try:
            trip_days = calculate_hohmann_transfer_time(departure, destination)
            self.trip_label.config(text=f"Trip Length: {trip_days} days")

            # Open the plot window
            self.open_plot_window()

            # Draw orbits and overlay mission
            self.draw_planetary_orbits()
            self.overlay_mission(departure, destination)

            # Start animation
            self.start_animation()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def open_plot_window(self):
        """Creates the Toplevel window for the orbital plot with scroll zoom."""
        if self.plot_window and tk.Toplevel.winfo_exists(self.plot_window):
            self.plot_window.destroy()

        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title("Orbital Plot Window")
        self.plot_window.geometry("900x700")

        plot_frame = ttk.Frame(self.plot_window, padding=10)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(fill=tk.X)

        self.planet_points.clear()

        # 🔹 Bind scroll event for zooming
        self.canvas.mpl_connect("scroll_event", self.on_scroll_zoom)

    def on_scroll_zoom(self, event):
        """Handles mouse wheel zoom in the orbital plot window."""
        base_scale = 1.1  # Scale factor for zooming
        if event.step > 0:  # Scrolled up (zoom in)
            scale_factor = 1 / base_scale
        else:  # Scrolled down (zoom out)
            scale_factor = base_scale

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        # Compute new limits
        new_xlim = [(x - x_center) * scale_factor + x_center for x in xlim]
        new_ylim = [(y - y_center) * scale_factor + y_center for y in ylim]

        # Apply zoom
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()

    def draw_planetary_orbits(self):
        """Plot orbits in the ax."""
        self.ax.clear()
        for planet, pdata in PLANETARY_DATA.items():
            radius = pdata["radius"]
            theta = np.linspace(0, 2 * np.pi, 300)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            self.ax.plot(x, y, label=f"{planet} Orbit")

        # Sun
        self.ax.scatter([0], [0], color='yellow', s=200, label='Sun')

        # Planet markers
        for planet, pdata in PLANETARY_DATA.items():
            (marker,) = self.ax.plot([pdata["radius"]], [0], 'o', markersize=8, label=planet)
            self.planet_points[planet] = marker

        self.ax.set_aspect('equal')
        self.ax.legend(loc='upper right', fontsize=8)
        self.canvas.draw()

    def overlay_mission(self, departure, destination):
        """Plot green dashed arc (Hohmann-like transfer)."""
        r1 = PLANETARY_DATA[departure]["radius"]
        r2 = PLANETARY_DATA[destination]["radius"]
        transfer_r = np.linspace(r1, r2, 300)
        theta = np.linspace(0, np.pi, 300)
        x = transfer_r * np.cos(theta)
        y = transfer_r * np.sin(theta)

        self.ax.plot(x, y, 'g--', linewidth=2, label="Transfer Arc")
        self.ax.legend(loc='upper right', fontsize=8)
        self.canvas.draw()

    def start_animation(self):
        """Start the orbital animation."""
        self.anim = start_animation(self.fig, self.planet_points)

