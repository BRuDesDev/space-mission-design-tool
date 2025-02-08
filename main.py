import tkinter as tk
from ttkbootstrap import Style
from gui import SpaceMissionGUI

if __name__ == "__main__":
    root = tk.Tk()

    # Set ttkbootstrap theme
    style = Style(theme='superhero')

    app = SpaceMissionGUI(root)
    root.mainloop()
