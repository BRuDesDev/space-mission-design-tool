import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from PIL import Image, ImageTk

# Approx. semi-major axes (AU) and orbital periods (days)
PLANETARY_DATA = {
    "Mercury": {"radius": 0.39, "period": 88.0},
    "Venus": {"radius": 0.72, "period": 225.0},
    "Earth": {"radius": 1.00, "period": 365.0},
    "Mars": {"radius": 1.52, "period": 687.0},
    "Jupiter": {"radius": 5.20, "period": 4331.0},
    "Saturn": {"radius": 9.58, "period": 10747.0},
    "Uranus": {"radius": 19.18, "period": 30589.0},
    "Neptune": {"radius": 30.07, "period": 59800.0}
}


class SpaceMissionGUI:
    LOGO_PATH = "logo/space-mission.png"  # Change to your actual file
    LOGO_WIDTH = 250  # Adjust to match your entry field area
    LOGO_HEIGHT = 250  # Adjust height as desired

    def __init__(self, root):
        self.root = root
        self.root.title("Space Mission Main Window")
        self.root.geometry("600x500")

        # Apply ttkbootstrap theme
        self.style = Style(theme='superhero')

        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Load & Display Logo
        self.load_logo(main_frame)

        # Planet Selections
        ttk.Label(main_frame, text="Select Departure Planet:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.departure_entry = ttk.Entry(main_frame, width=30)
        self.departure_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(main_frame, text="Select Destination Planet:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.destination_entry = ttk.Entry(main_frame, width=30)
        self.destination_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Calculate Mission
        calc_button = ttk.Button(main_frame, text="Calculate Mission", command=self.calculate_mission)
        calc_button.grid(row=3, column=1, pady=10, sticky="w")

        # Trip label
        self.trip_label = ttk.Label(main_frame, text="Trip Length: --", font=("Arial", 12, "bold"))
        self.trip_label.grid(row=4, column=0, columnspan=2, pady=10)

        # 5) Animation toggle (still in main window)
        self.animate_button = ttk.Button(main_frame, text="Start Animation", command=self.toggle_animation)
        self.animate_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Toplevel references
        self.plot_window = None
        self.fig_tl = None
        self.ax_tl = None
        self.canvas_tl = None
        self.toolbar_tl = None
        self.planet_points = {}
        self.anim_tl = None
        self.is_animating = False

    def load_logo(self, parent):
        """Load and resize the logo, place it in row=0 across two columns."""
        try:
            original_logo = Image.open(self.LOGO_PATH)
            resized_logo = original_logo.resize((self.LOGO_WIDTH, self.LOGO_HEIGHT), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(resized_logo)
        except Exception as e:
            messagebox.showwarning("Logo Warning", f"Could not load logo: {e}")
            self.logo_img = None

        if self.logo_img:
            logo_label = ttk.Label(parent, image=self.logo_img)
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

    def calculate_mission(self):
        """Check input, compute trip length, open the Toplevel plot window."""
        departure = self.departure_entry.get().strip().title()
        destination = self.destination_entry.get().strip().title()

        if departure not in PLANETARY_DATA or destination not in PLANETARY_DATA:
            messagebox.showerror("Error", "Invalid planet name!")
            return
        if departure == destination:
            messagebox.showwarning("Warning", "Pick different planets!")
            return

        # Calculate a rough Hohmann transfer time
        r1 = PLANETARY_DATA[departure]["radius"]
        r2 = PLANETARY_DATA[destination]["radius"]
        trip_time_years = np.pi * np.sqrt(((r1 + r2) ** 3) / (8 * 1.0))
        trip_days = round(trip_time_years * 365, 1)
        self.trip_label.config(text=f"Trip Length: {trip_days} days")

        # Create the Toplevel for plotting
        self.open_plot_window()

        # Draw orbits & overlay mission
        self.draw_planetary_orbits_tl()
        self.overlay_mission_tl(r1, r2)

        # Start animation automatically
        self.start_animation()

    def open_plot_window(self):
        """Create or recreate the Toplevel window for the orbital plot."""
        if self.plot_window and tk.Toplevel.winfo_exists(self.plot_window):
            self.plot_window.destroy()

        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title("Orbital Plot Window")
        self.plot_window.geometry("900x700")

        plot_frame = ttk.Frame(self.plot_window, padding=10)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        self.fig_tl, self.ax_tl = plt.subplots(figsize=(6, 6))
        self.canvas_tl = FigureCanvasTkAgg(self.fig_tl, master=plot_frame)
        self.canvas_tl.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.toolbar_tl = NavigationToolbar2Tk(self.canvas_tl, plot_frame, pack_toolbar=False)
        self.toolbar_tl.update()
        self.toolbar_tl.pack(fill=tk.X)

        # Connect scroll event for wheel zoom
        self.canvas_tl.mpl_connect("scroll_event", self.on_scroll)

        self.planet_points.clear()
        self.anim_tl = None
        self.is_animating = False

    def draw_planetary_orbits_tl(self):
        """Plot orbits on ax_tl and create planet markers at angle=0."""
        self.ax_tl.clear()

        for planet, pdata in PLANETARY_DATA.items():
            radius = pdata["radius"]
            theta = np.linspace(0, 2 * np.pi, 300)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            self.ax_tl.plot(x, y, label=f"{planet} Orbit")

        # Sun
        self.ax_tl.scatter([0], [0], color='yellow', s=200, label='Sun')

        # Markers
        for planet, pdata in PLANETARY_DATA.items():
            (marker,) = self.ax_tl.plot([pdata["radius"]], [0], 'o', markersize=8, label=planet)
            self.planet_points[planet] = marker

        max_r = max(p["radius"] for p in PLANETARY_DATA.values()) * 1.4
        self.ax_tl.set_xlim(-max_r, max_r)
        self.ax_tl.set_ylim(-max_r, max_r)
        self.ax_tl.set_aspect('equal')
        self.ax_tl.set_xlabel("AU")
        self.ax_tl.set_ylabel("AU")
        self.ax_tl.set_title("Planetary Orbits - Toplevel")
        self.ax_tl.legend(loc='upper right', fontsize=8)

        self.canvas_tl.draw()

    def overlay_mission_tl(self, r1, r2):
        """Plot green dashed arc (Hohmann-like)."""
        transfer_r = np.linspace(r1, r2, 300)
        theta = np.linspace(0, np.pi, 300)
        x = transfer_r * np.cos(theta)
        y = transfer_r * np.sin(theta)

        self.ax_tl.plot(x, y, 'g--', linewidth=2, label="Transfer Arc")
        self.ax_tl.legend(loc='upper right', fontsize=8)
        self.canvas_tl.draw()

    def animate_frame(self, frame):
        """Update planet positions in the Toplevel figure."""
        dt_days = 10
        current_time = frame * dt_days

        for planet, marker in self.planet_points.items():
            radius = PLANETARY_DATA[planet]["radius"]
            period_days = PLANETARY_DATA[planet]["period"]
            angle = 2 * np.pi * (current_time / period_days)
            marker.set_data([radius * np.cos(angle)], [radius * np.sin(angle)])
        return list(self.planet_points.values())

    def toggle_animation(self):
        """Start/stop the animation from the main window button."""
        if not self.plot_window or not tk.Toplevel.winfo_exists(self.plot_window):
            messagebox.showinfo("Info", "No plot window open! Calculate a mission first.")
            return

        if self.is_animating:
            # Stop
            if self.anim_tl:
                self.anim_tl.event_source.stop()
            self.is_animating = False
            self.animate_button.config(text="Start Animation")
        else:
            # Start
            self.start_animation()

    def start_animation(self):
        """Helper to start the FuncAnimation if not already animating."""
        if not self.is_animating:
            self.anim_tl = FuncAnimation(
                self.fig_tl,
                self.animate_frame,
                frames=1000,
                interval=50,
                blit=False,
                repeat=True
            )
            self.is_animating = True
            self.animate_button.config(text="Stop Animation")

    def on_scroll(self, event):
        """Mouse-wheel zoom in the Toplevel figure."""
        if not self.ax_tl:
            return

        base_scale = 1.1
        if event.step > 0:  # scrolled up => zoom in
            scale_factor = 1 / base_scale
        else:
            scale_factor = base_scale

        xlim = self.ax_tl.get_xlim()
        ylim = self.ax_tl.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        new_xlim = [(x - x_center) * scale_factor + x_center for x in xlim]
        new_ylim = [(y - y_center) * scale_factor + y_center for y in ylim]

        self.ax_tl.set_xlim(new_xlim)
        self.ax_tl.set_ylim(new_ylim)
        self.canvas_tl.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceMissionGUI(root)
    root.mainloop()
