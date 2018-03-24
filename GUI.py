from tkinter import *
from PIL import Image, ImageTk


def genImage(path):
    img = Image.open(path)
    processed_img = ImageTk.PhotoImage(img)
    return processed_img


class GUI(object):

    def __init__(self, master):
        self.master = master
        self.tiles = []

        image_dict = {
            'unexp': genImage('./sprites/unexp.jpg'),
            'exp_blank': genImage('./sprites/exp_blank.jpg')
        }

        def clicked(event):
            tile.configure(image=image_dict['exp_blank'])

        for x in range(30):
            for y in range(16):
                tile = Label(master, image=image_dict['unexp'], borderwidth=0)
                tile.image = image_dict['unexp']
                tile.grid(row=y, column=x)
                tile.bind('<Button-1>', clicked)
                self.tiles.append(tile)


root = Tk()
gui = GUI(root)
root.mainloop()