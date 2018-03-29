import tkinter as tk
from PIL import Image, ImageTk


def gen_image(path):
    img = Image.open(path)
    processed_img = ImageTk.PhotoImage(img)
    return processed_img


def place_ele(master, img, x, y):
    widget = tk.Label(master, image=img, borderwidth=0)
    widget.image = img
    widget.grid(column=x, row=y)
    return widget


class Input(object):

    def __init__(self):
        self.pressed = False
        self.current = None
        self.label_dict = dict()


class CoreTile(object):

    def __init__(self, master, input_holder, column, row):
        self.Input = input_holder
        self.mouse = None
        self.master = master
        self.column = column
        self.row = row
        self.img_unexp = gen_image('./sprites/unexp.jpg')
        self.img_exp_blank = gen_image('./sprites/exp_blank.jpg')
        self.Label = tk.Label(self.master, borderwidth=0, image=self.img_unexp)
        self.Label.image = self.img_unexp
        self.id = self.Label.winfo_id()

        self.Input.label_dict[self.id] = self

        self.Label.bind('<Enter>', self.mouse_enter)
        self.Label.bind('<Leave>', self.mouse_leave)
        self.Label.bind('<ButtonPress-1>', self.press_click)
        self.Label.bind('<ButtonRelease-1>', self.release_click)

    def __repr__(self):
        return str(self.column) + ' ' + str(self.row)

    def press(self):
        self.Label.configure(image=self.img_exp_blank)

    def relieve(self):
        self.Label.configure(image=self.img_unexp)

    def mouse_enter(self, event):
        self.mouse = True
        if self.Input.pressed:
            self.press()

    def mouse_leave(self, event):
        self.mouse = False
        if self.Input.pressed:
            self.relieve()

    def press_click(self, event):
        self.Input.pressed = True
        self.press()

    def release_click(self, event):
        self.Input.pressed = False
        if self.mouse:
            self.press()
        else:
            self.relieve()


class GUI(object):

    def __init__(self, master, info):
        self.master = master
        self.tiles = {}
        self.info = info

        image_dict = {
            'unexp': gen_image('./sprites/unexp.jpg'),
            'exp_blank': gen_image('./sprites/exp_blank.jpg'),
            'border_LR': gen_image('./sprites/border_LR.jpg'),
            'border_TB': gen_image('./sprites/border_TB.jpg'),
            'border_TLcorner': gen_image('./sprites/border_TLcorner.jpg'),
            'border_TRcorner': gen_image('./sprites/border_TRcorner.jpg'),
            'border_BLcorner': gen_image('./sprites/border_BLcorner.jpg'),
            'border_BRcorner': gen_image('./sprites/border_BRcorner.jpg'),
        }

        for x in [0, 31]:
            for y in range(1, 17):
                place_ele(master, image_dict['border_LR'], x, y)

        for x in range(1, 31):
            for y in [0, 17]:
                place_ele(master, image_dict['border_TB'], x, y)

        place_ele(master, image_dict['border_TRcorner'], 31, 0)
        place_ele(master, image_dict['border_TLcorner'], 0, 0)
        place_ele(master, image_dict['border_BRcorner'], 31, 17)
        place_ele(master, image_dict['border_BLcorner'], 0, 17)

        for x in range(1, 31):
            for y in range(1, 17):
                tile = CoreTile(master, self.info, x, y)
                tile.Label.grid(column=x, row=y)
                self.tiles[(x, y)] = tile


class Root(object):

    def __init__(self, input):
        self.input = input
        self.root = tk.Tk()

        self.root.bind('<Motion>', self.mouse_motion)

    def mouse_motion(self, event):
        x, y = self.root.winfo_pointerxy()
        new_id = self.root.winfo_containing(x, y).winfo_id()
        if new_id in self.input.label_dict and new_id != self.input.current:
            if self.input.current is not None:
                self.input.current.Label.event_generate('<Leave>')
            self.input.current = self.input.label_dict[new_id]
            self.input.current.Label.event_generate('<Enter>')


info_holder = Input()
root = Root(info_holder)
gui = GUI(root.root, info_holder)
root.root.mainloop()