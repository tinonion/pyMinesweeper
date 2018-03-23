from tkinter import *


class Grid(object):

    def __init__(self, master):
        self.master = master

        self.tiles = []

        for x in range(30):
            for y in range(16):
                tile = Button(master, text='t')
                self.tiles.append(tile)
                tile.grid(row=y, column=x)


root = Tk()
gui = Grid(root)
root.mainloop()