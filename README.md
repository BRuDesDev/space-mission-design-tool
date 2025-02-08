![image](https://github.com/user-attachments/assets/671c92e9-43f1-46c1-8d1c-b47f6d09dc6d)

## Space Mission Design Tool

# Overview

The **Space Mission Design Tool** is a Python application that calculates and visualizes interplanetary missions. Using real-world planetary data, it helps users design and plan missions by estimating delta-V requirements, launch windows, travel time, and more. The tool features a Tkinter-based GUI (with ttkbootstrap styling) and a Matplotlib-powered orbit plot.

# Features

**Hohmann Transfer Calculation**: Computes the delta-V needed to travel between two planetary orbits.

**Real Planetary Data**: Fetches real-world planetary masses, radii, and orbital periods.

**Orbit Visualization**: Displays planets, orbits, and transfer arcs with Matplotlib.

**GUI Interface**: A modern Tkinter window (styled via ttkbootstrap) for user input and mission results.

**Simulated Orbiting**: The planets will animate and orbit the sun at the correct distance and speed ratio

# **Installation and Use**

1. Clone the Repository:

       $ git clone https://github.com/yourusername/space_mission_tool.git

       $ cd space_mission_tool

2. Create a Virtual Environment (recommended):
 
       $ python -m venv venv
 
       $ source venv/bin/activate  # On Linux/Mac
      
       $ venv\Scripts\activate    # On Windows

3. Install Dependencies:

       $ pip install -r requirements.txt

5. Run Main Script:

       $ python3 main.py

----------------------------------------------

Follow the On-Screen Prompts:

    Enter a departure planet (e.g., Earth).

    Enter a destination planet (e.g., Mars).

    Click Calculate Mission to see results.

    A Matplotlib plot window appears, showing orbits and any computed transfer arcs.

