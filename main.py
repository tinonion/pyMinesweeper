import gui
import tkinter as tk

# Pulls elements from all other project files to construct the master window, GUI and main event loop
root = tk.Tk()
root.title('pySweeper')
info_holder = gui.Info(root)
gui = gui.GUI(root, info_holder)
root.mainloop()

