import tkinter as tk
from PIL import Image, ImageTk


def genImage(path):
    img = Image.open(path)
    processed_img = ImageTk.PhotoImage(img)
    return processed_img


def placeEle(master, img, x, y):
    widget = tk.Label(master, image=img, borderwidth=0)
    widget.image = img
    widget.grid(column=x, row=y)
    return widget


class Input(object):

    def __init__(self):
        self.pressed = False


class CoreTile(object):

    def __init__(self, master, input_holder):
        self.img_unexp = genImage('./sprites/unexp.jpg')
        self.img_exp_blank = genImage('./sprites/exp_blank.jpg')
        self.Label = tk.Label(master, borderwidth=0, image=self.img_unexp)
        self.Label.image = self.img_unexp
        self.Input = input_holder
        self.mouse = None

        def mouseEnter(event):
            self.mouse = True
            if self.Input.pressed:
                self.Label.configure(image=self.img_exp_blank)

        def mouseLeave(event):
            self.mouse = False
            print(self.Label.winfo_pointerxy())
            if self.Input.pressed:
                self.Label.configure(image=self.img_unexp)

        def pressClick(event):
            self.Input.pressed = True
            self.Label.configure(image=self.img_exp_blank)

        def releaseClick(event):
            self.Input.pressed = False
            if self.mouse:
                self.Label.configure(image=self.img_exp_blank)
            else:
                self.Label.configure(image=self.img_unexp)

        def pressedEnter(event):
            self.Label.configure(image=self.img_exp_blank)

        self.Label.bind('<Enter>', mouseEnter)
        self.Label.bind('<Leave>', mouseLeave)
        self.Label.bind('<ButtonPress-1>', pressClick)
        self.Label.bind('<ButtonRelease-1>', releaseClick)


class GUI(object):

    def __init__(self, master):
        self.master = master
        self.tiles = []

        image_dict = {
            'unexp': genImage('./sprites/unexp.jpg'),
            'exp_blank': genImage('./sprites/exp_blank.jpg'),
            'border_LR': genImage('./sprites/border_LR.jpg'),
            'border_TB': genImage('./sprites/border_TB.jpg'),
            'border_TLcorner': genImage('./sprites/border_TLcorner.jpg'),
            'border_TRcorner': genImage('./sprites/border_TRcorner.jpg'),
            'border_BLcorner': genImage('./sprites/border_BLcorner.jpg'),
            'border_BRcorner': genImage('./sprites/border_BRcorner.jpg'),
        }

        for x in [0, 31]:
            for y in range(1, 17):
                placeEle(master, image_dict['border_LR'], x, y)

        for x in range(1, 31):
            for y in [0, 17]:
                placeEle(master, image_dict['border_TB'], x, y)

        placeEle(master, image_dict['border_TRcorner'], 31, 0)
        placeEle(master, image_dict['border_TLcorner'], 0, 0)
        placeEle(master, image_dict['border_BRcorner'], 31, 17)
        placeEle(master, image_dict['border_BLcorner'], 0, 17)

        pressed = Input()

        for x in range(1, 31):
            for y in range(1, 17):
                tile = CoreTile(master, pressed)
                tile.Label.grid(column=x, row=y)
                self.tiles.append(tile)


root = tk.Tk()
gui = GUI(root)
root.mainloop()